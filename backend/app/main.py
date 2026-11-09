
import os
import secrets
from datetime import datetime, timedelta, timezone, date
from decimal import Decimal, ROUND_HALF_UP
import logging

logger = logging.getLogger(__name__)
from fastapi import (
    FastAPI, Depends, HTTPException, status
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from jose import jwt, JWTError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import (
    User, Lead, Quote, Project, StageHistory,
    SubsidyRule, PriceRule, TariffRule, TariffSlab
)
from app.models.project import PROJECT_STAGES
from app.db.base import Base
from app.core.database import engine
from fastapi import UploadFile, File
from app.models import Bill
from app.services.bill_service import (
    validate_bill_file,
    extract_bill_fields,
    UPLOAD_DIR,
)

# --------------------------------------------------
# APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Surya Setu API",
    description="Rooftop solar lead and quotation management",
    version="1.0.0",
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
password_context = PasswordHasher()
ALGORITHM = "HS256"


# --------------------------------------------------
# DATABASE / AUTH HELPERS
# --------------------------------------------------

def get_password_hash(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return password_context.verify(hashed, password)
    except (VerifyMismatchError, VerificationError):
        return False
def create_access_token(user: User) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": expires,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise credentials_error

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise credentials_error

    return user


def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Administrator access required",
        )
    return user


def latest_rule(db, model, quote_date):
    rule = (
        db.query(model)
        .filter(model.effective_from <= quote_date)
        .order_by(model.effective_from.desc())
        .first()
    )

    if not rule:
        raise HTTPException(
            status_code=400,
            detail=f"No effective {model.__name__} configured for this date",
        )

    return rule


# --------------------------------------------------
# REQUEST SCHEMAS
# --------------------------------------------------

class LeadCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    phone: str = Field(pattern=r"^[6-9][0-9]{9}$")
    owner_or_tenant: str
    roof_type: str = Field(min_length=2, max_length=50)
    roof_area: Decimal = Field(gt=0)
    monthly_bill: Decimal = Field(ge=0)
    pincode: str = Field(pattern=r"^[0-9]{6}$")
    language: str = "en"
    consent: bool


class QuoteCreate(BaseModel):
    monthly_units: Decimal = Field(gt=0)


class StageUpdate(BaseModel):
    stage: str
    note: str | None = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10)
    role: str = "sales"


class BillConfirmation(BaseModel):
    consumer_no: str | None = Field(default=None, max_length=100)
    tariff: str | None = Field(default=None, max_length=100)
    sanctioned_load: Decimal | None = Field(default=None, ge=0)
    monthly_units: Decimal = Field(gt=0)


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {
            "success": True,
            "database": "connected",
            "time": datetime.now(timezone.utc).isoformat(),
        }
    except Exception:
        raise HTTPException(503, "Database unavailable")


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

@app.post("/api/auth/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == form.username.lower())
        .first()
    )

    if not user or not verify_password(
        form.password, user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        },
    }


@app.post("/api/auth/users", status_code=201)
def create_staff_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if data.role not in ("admin", "sales"):
        raise HTTPException(400, "Invalid staff role")

    email = str(data.email).lower()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "Email already registered")

    user = User(
        email=email,
        password_hash=get_password_hash(data.password),
        role=data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "email": user.email, "role": user.role}


# --------------------------------------------------
# LEADS
# --------------------------------------------------

@app.post("/api/leads", status_code=201)
def create_lead(
    data: LeadCreate,
    db: Session = Depends(get_db),
):
    if not data.consent:
        raise HTTPException(
            400,
            "Consent is required before submitting a lead",
        )

    if data.owner_or_tenant not in ("owner", "tenant"):
        raise HTTPException(400, "Invalid ownership type")

    lead = Lead(
        public_token=secrets.token_urlsafe(32),
        name=data.name.strip(),
        phone=data.phone,
        owner_or_tenant=data.owner_or_tenant,
        roof_type=data.roof_type,
        roof_area=data.roof_area,
        monthly_bill=data.monthly_bill,
        pincode=data.pincode,
        language=data.language,
        consent_given_at=datetime.now(timezone.utc),
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return {
        "success": True,
        "lead_id": lead.id,
        "public_token": lead.public_token,
        "message": "Lead created successfully",
    }


@app.get("/api/leads")
def list_leads(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    leads = (
        db.query(Lead)
        .order_by(Lead.created_at.desc())
        .all()
    )

    return [
        {
            "id": lead.id,
            "name": lead.name,
            "phone": "******" + lead.phone[-4:],
            "owner_or_tenant": lead.owner_or_tenant,
            "monthly_bill": float(lead.monthly_bill),
            "score": lead.score,
            "recommended_kw": lead.recommended_kw,
            "created_at": lead.created_at.isoformat(),
        }
        for lead in leads
    ]


@app.get("/api/leads/{lead_id}")
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(404, "Lead not found")

    return {
        "id": lead.id,
        "name": lead.name,
        "phone": lead.phone,
        "owner_or_tenant": lead.owner_or_tenant,
        "roof_type": lead.roof_type,
        "roof_area": float(lead.roof_area),
        "monthly_bill": float(lead.monthly_bill),
        "pincode": lead.pincode,
        "score": lead.score,
        "score_reason": lead.score_reason,
        "recommended_kw": lead.recommended_kw,
        "next_step": lead.next_step,
    }


# --------------------------------------------------
# SOLAR QUOTATION
# --------------------------------------------------

@app.post("/api/leads/{lead_id}/quote", status_code=201)
def create_quote(
    lead_id: int,
    data: QuoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(404, "Lead not found")

    today = date.today()

    generation_per_kw = Decimal("1400")

    setting = db.query(__import__(
        "app.models.rules", fromlist=["Setting"]
    ).Setting).filter_by(key="generation_per_kw").first()

    if setting:
        generation_per_kw = Decimal(setting.value)

    annual_units = data.monthly_units * Decimal("12")
    raw_kw = annual_units / generation_per_kw
    kw = max(
        1,
        int(raw_kw.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
    )

    subsidy_rule = latest_rule(db, SubsidyRule, today)
    price_rule = latest_rule(db, PriceRule, today)
    tariff_rule = latest_rule(db, TariffRule, today)

    first_kw = min(kw, subsidy_rule.first_kw_count)
    remaining_kw = max(0, kw - subsidy_rule.first_kw_count)

    subsidy = (
        Decimal(first_kw) * subsidy_rule.per_kw_first
        + Decimal(remaining_kw) * subsidy_rule.extra_kw_amount
    )

    subsidy = min(subsidy, subsidy_rule.cap)

    system_price = Decimal(kw) * price_rule.price_per_kw
    net_cost = max(Decimal("0"), system_price - subsidy)

    slabs = (
        db.query(TariffSlab)
        .filter(TariffSlab.tariff_rule_id == tariff_rule.id)
        .order_by(TariffSlab.min_units)
        .all()
    )

    if not slabs:
        raise HTTPException(
            400,
            "No tariff slabs configured for the selected tariff",
        )

    remaining_units = data.monthly_units
    monthly_bill_estimate = Decimal("0")

    for slab in slabs:
        if remaining_units <= 0:
            break

        slab_capacity = (
            Decimal(slab.max_units - slab.min_units + 1)
            if slab.max_units is not None
            else remaining_units
        )

        units_in_slab = min(remaining_units, slab_capacity)

        rate = slab.energy_charge + slab.wheeling_charge
        monthly_bill_estimate += units_in_slab * rate
        remaining_units -= units_in_slab

    effective_tariff = (
        monthly_bill_estimate / data.monthly_units
    )

    yearly_generation = Decimal(kw) * generation_per_kw
    yearly_savings = yearly_generation * effective_tariff

    payback_years = (
        net_cost / yearly_savings
        if yearly_savings > 0
        else None
    )

    snapshot = {
        "system_kw": kw,
        "monthly_units": str(data.monthly_units),
        "annual_units": str(annual_units),
        "generation_per_kw": str(generation_per_kw),
        "system_price": str(system_price),
        "subsidy": str(subsidy),
        "net_cost": str(net_cost),
        "effective_tariff": str(effective_tariff),
        "yearly_generation": str(yearly_generation),
        "estimated_yearly_savings": str(yearly_savings),
        "estimated_payback_years": (
            str(payback_years) if payback_years is not None else None
        ),
        "subsidy_note": (
            "Subject to PM Surya Ghar eligibility and approval. "
            "This is an estimate, not a guaranteed benefit."
        ),
        "assumptions": [
            "Generation is assumed at 1400 units per kW annually.",
            "Savings use an estimated effective slab tariff.",
            "Actual savings depend on self-consumption and net metering.",
        ],
    }

    quote = Quote(
        lead_id=lead.id,
        options_json=snapshot,
        subsidy_rule_id=subsidy_rule.id,
        price_rule_id=price_rule.id,
        tariff_rule_id=tariff_rule.id,
        created_by=user.id,
    )

    lead.recommended_kw = kw

    threshold_setting = db.query(
        __import__("app.models.rules", fromlist=["Setting"]).Setting
    ).filter_by(key="score_bill_threshold").first()

    threshold = Decimal(
        threshold_setting.value if threshold_setting else "1000"
    )

    if lead.owner_or_tenant == "tenant":
        lead.score = "Low"
        lead.score_reason = "tenant"
    elif lead.monthly_bill < threshold:
        lead.score = "Low"
        lead.score_reason = "small bill"
    else:
        lead.score = "High"
        lead.score_reason = "eligible for survey assessment"

    lead.next_step = (
        "short_call" if lead.score == "Low" else "survey_visit"
    )

    db.add(quote)
    db.commit()
    db.refresh(quote)

    return {
        "quote_id": quote.id,
        "lead_id": lead.id,
        "quotation": snapshot,
    }


# --------------------------------------------------
# PROJECT TRACKING
# --------------------------------------------------

@app.post("/api/quotes/{quote_id}/project", status_code=201)
def create_project(
    quote_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()

    if not quote:
        raise HTTPException(404, "Quote not found")

    existing = db.query(Project).filter(
        Project.quote_id == quote_id
    ).first()

    if existing:
        raise HTTPException(409, "Project already exists")

    token = secrets.token_urlsafe(32)

    project = Project(
        quote_id=quote.id,
        public_token=token,
        stage=PROJECT_STAGES[0],
    )

    db.add(project)
    db.flush()

    history = StageHistory(
        project_id=project.id,
        stage=PROJECT_STAGES[0],
        changed_by=user.id,
        note="Project created",
    )

    db.add(history)
    db.commit()
    db.refresh(project)

    return {
        "project_id": project.id,
        "public_status_token": project.public_token,
        "stage": project.stage,
    }


@app.patch("/api/projects/{project_id}/stage")
def update_project_stage(
    project_id: int,
    data: StageUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if data.stage not in PROJECT_STAGES:
        raise HTTPException(400, "Invalid project stage")

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    project.stage = data.stage
    project.updated_at = datetime.now(timezone.utc)

    history = StageHistory(
        project_id=project.id,
        stage=data.stage,
        changed_by=user.id,
        note=data.note,
    )

    db.add(history)
    db.commit()

    return {"success": True, "stage": project.stage}


@app.get("/api/public/status/{token}")
def public_project_status(
    token: str,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(
        Project.public_token == token
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    history = (
        db.query(StageHistory)
        .filter(StageHistory.project_id == project.id)
        .order_by(StageHistory.changed_at.asc())
        .all()
    )

    return {
        "current_stage": project.stage,
        "updated_at": project.updated_at.isoformat(),
        "timeline": [
            {
                "stage": item.stage,
                "date": item.changed_at.isoformat(),
                "note": item.note,
            }
            for item in history
        ],
    }


@app.post("/api/leads/{lead_id}/bill/upload", status_code=201)
async def upload_bill(
    lead_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(404, "Lead not found")

    content = await file.read()

    try:
        extension = validate_bill_file(
            file.content_type,
            content,
        )
    except ValueError as error:
        raise HTTPException(400, str(error))

    filename = secrets.token_hex(16) + extension
    path = UPLOAD_DIR / filename
    path.write_bytes(content)

    bill = Bill(
        lead_id=lead_id,
        image_path=str(path),
        status="uploaded",
        extraction_attempts=0,
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)
    saved_bill_id = bill.id

    try:
        extracted = extract_bill_fields(str(path))

        bill.consumer_no = (
            extracted["consumer_no"]["value"]
        )
        bill.tariff = extracted["tariff"]["value"]

        load = extracted["sanctioned_load"]["value"]
        units = extracted["monthly_units"]["value"]

        bill.sanctioned_load = (
            float(load) if load is not None else None
        )
        bill.monthly_units = (
            float(units) if units is not None else None
        )

        bill.confidences_json = {
            key: value["confidence"]
            for key, value in extracted.items()
        }

        bill.confirmed_values_json = extracted
        bill.extraction_attempts = 1
        bill.status = "extracted"

        db.commit()

        return {
            "bill_id": bill.id,
            "status": bill.status,
            "extracted_fields": extracted,
            "message": "Please review extracted values before confirmation",
        }

    
    except Exception:
        logger.exception("Bill AI extraction failed")

        db.rollback()

        bill = db.query(Bill).filter(
            Bill.id == saved_bill_id
        ).first()

        if bill:
            bill.status = "manual_required"
            bill.extraction_attempts = 1
            db.commit()

        return {
            "bill_id": saved_bill_id,
            "status": "manual_required",
            "message": (
                "AI extraction failed. "
                "Please enter bill details manually."
            ),
        }

# --------------------------------------------------
# MANUAL BILL CONFIRMATION
# --------------------------------------------------

@app.put("/api/bills/{bill_id}/confirm")
def confirm_bill(
    bill_id: int,
    data: BillConfirmation,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    bill.consumer_no = data.consumer_no.strip() if data.consumer_no else None
    bill.tariff = data.tariff.strip() if data.tariff else None
    bill.sanctioned_load = (
        float(data.sanctioned_load)
        if data.sanctioned_load is not None
        else None
    )
    bill.monthly_units = float(data.monthly_units)
    bill.confirmed_values_json = {
        "consumer_no": bill.consumer_no,
        "tariff": bill.tariff,
        "sanctioned_load": (
            str(data.sanctioned_load)
            if data.sanctioned_load is not None
            else None
        ),
        "monthly_units": str(data.monthly_units),
    }
    bill.confirmed_by_user = True
    bill.confirmed_at = datetime.now(timezone.utc)
    bill.status = "confirmed"

    db.commit()
    db.refresh(bill)

    return {
        "success": True,
        "message": "Bill details confirmed",
        "bill_id": bill.id,
        "status": bill.status,
        "monthly_units": bill.monthly_units,
    }

