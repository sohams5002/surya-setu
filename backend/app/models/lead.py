
"""
Homeowner lead database model.
"""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Numeric,
    Boolean,
    DateTime,
    CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Lead(Base):

    __tablename__ = "leads"

    __table_args__ = (
        CheckConstraint(
            "owner_or_tenant IN ('owner', 'tenant')",
            name="ck_leads_ownership"
        ),
        CheckConstraint(
            "monthly_bill >= 0",
            name="ck_leads_monthly_bill"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    public_token: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        String(15),
        nullable=False
    )

    owner_or_tenant: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    roof_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    roof_area: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    monthly_bill: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    pincode: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
        index=True
    )

    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en"
    )

    consent_given_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    score: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    score_reason: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    recommended_kw: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    next_step: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
