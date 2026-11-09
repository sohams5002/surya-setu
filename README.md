# Surya Setu

**Rooftop solar enquiry and quotation management for Nagpur and the Vidarbha region.**

Surya Setu is a staff-facing application for recording homeowner enquiries, reviewing electricity-bill details, preparing indicative rooftop-solar quotations, and tracking projects through installation and subsidy milestones.

## What it does

- Staff sign-in with JWT authentication.
- Enquiry capture with customer consent, property ownership, roof details, monthly bill, pincode, and preferred language.
- Lead list with priority indicators and masked phone numbers.
- Electricity-bill image upload with an AI extraction attempt and a manual-entry fallback.
- Staff confirmation of bill details before using monthly units for a quotation.
- Solar system sizing based on annual consumption and a configurable generation assumption.
- Date-effective subsidy, system-price, and electricity-tariff rules.
- Indicative quotation calculations, including system price, subsidy estimate, net cost, estimated annual savings, and payback.
- Quotation snapshot stored with the rule IDs used to calculate it.
- Project creation and stage history, with a public status API that exposes project progress without customer details.
- Browser print flow for saving a generated quotation view as PDF.

## Technology

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite for local development; PostgreSQL can be used for deployment
- Alembic migrations
- JWT authentication
- Argon2 password hashing
- Pydantic validation
- pytest

### Frontend
- React
- Vite
- Axios
- React Router package (available in the frontend dependencies)
- lucide-react
- CSS

## Project structure

```text
surya-setu/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuration and database connection
│   │   ├── db/            # SQLAlchemy base / seed helpers
│   │   ├── logic/         # Sizing, subsidy, payback and scoring logic
│   │   ├── models/        # SQLAlchemy models
│   │   ├── services/      # Electricity bill extraction and validation
│   │   └── main.py        # FastAPI application and API routes
│   ├── migrations/        # Alembic migrations
│   ├── tests/             # Automated tests
│   ├── requirements.txt
│   ├── alembic.ini
│   └── seed_tariffs.py
├── frontend/
│   ├── src/
│   ├── index.html
│   └── package.json
├── docs/
├── .env.example
└── README.md
```

## Requirements

- Python 3.11 or later (use a Python version supported by the installed dependencies)
- Node.js and npm
- Git

## Local setup

Run the backend and frontend in separate terminal windows.

### 1. Clone the repository

```bash
git clone https://github.com/sohams5002/surya-setu.git
cd surya-setu
```

### 2. Configure environment variables

Copy the example file:

```bash
cp .env.example .env
```

Review `.env.example` and set a unique `SECRET_KEY`, database URL, and any optional bill-extraction credentials required by your local configuration. Never commit `.env`.

The application uses SQLite by default if no database URL is supplied. For PostgreSQL, configure the database URL according to the settings in `backend/app/core/config.py`.

### 3. Install and prepare the backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Run migrations:

```bash
cd backend
alembic upgrade head
```

Seed the demonstration tariff slabs:

```bash
python seed_tariffs.py
```

Create or reset a staff administrator using the repository's admin utility scripts and the environment variables they expect. Set a strong password; do not put credentials in source code.

Start the API:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API health check:

- `http://127.0.0.1:8000/api/health`

Interactive API documentation:

- `http://127.0.0.1:8000/docs`

### 4. Install and start the frontend

In another terminal:

```bash
cd surya-setu/frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally:

- `http://localhost:5173`

The frontend API base URL is currently configured in `frontend/src/App.jsx` as `http://127.0.0.1:8000`. Update it for a deployed API before deployment.

## Main API routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/health` | API and database health |
| POST | `/api/auth/login` | Staff login |
| POST | `/api/auth/users` | Create staff user (admin only) |
| GET | `/api/leads` | List enquiries (staff only) |
| POST | `/api/leads` | Create enquiry |
| GET | `/api/leads/{lead_id}` | Get enquiry details (staff only) |
| POST | `/api/leads/{lead_id}/bill/upload` | Upload electricity-bill image (staff only) |
| PUT | `/api/bills/{bill_id}/confirm` | Confirm extracted or manually entered bill fields (staff only) |
| POST | `/api/leads/{lead_id}/quote` | Generate and save a quotation snapshot (staff only) |
| POST | `/api/quotes/{quote_id}/project` | Create a tracked project (staff only) |
| PATCH | `/api/projects/{project_id}/stage` | Update project stage (staff only) |
| GET | `/api/public/status/{token}` | Read public project progress |

All staff-only routes require a bearer token obtained from the login endpoint.

## Business rules and calculation notes

### Solar system size

The sizing estimate uses annual electricity consumption and a configurable annual generation assumption per installed kW. The current default assumption is **1,400 units per kW per year**. The calculated size is rounded to a whole kW using half-up rounding, with a minimum of 1 kW.

### Subsidy

Subsidy values are selected from the latest subsidy rule effective on the quotation date. The current demonstration rule structure supports a per-kW amount for the first specified number of kW, an additional amount for subsequent kW, and a maximum cap.

Subsidy is an estimate only. Actual eligibility, system capacity, vendor requirements, and disbursement are subject to the applicable PM Surya Ghar scheme rules and official approval.

### System price

The system price is selected from the latest price rule effective on the quotation date. The demonstration price must be reviewed and replaced with the installer's actual commercial price before real customer use.

### Electricity tariff and savings

The quotation estimates an effective rate using configured progressive tariff slabs. The seeded FY 2026–27 residential slabs are demonstration data and must be checked against the applicable current MSEDCL tariff order and the customer's actual bill.

Actual bills can include fixed charges, electricity duty, FAC and other components. Real savings also depend on generation, self-consumption, export credits, net-metering arrangements, and site conditions. Savings and payback shown by the application are indicative, not guaranteed.

### Lead priority

Lead priority is a follow-up aid, not an eligibility decision. Tenant enquiries and enquiries below the configured monthly-bill threshold are marked Low; other enquiries are marked High. Low priority does not automatically reject an enquiry.

### Project stages

Projects move through the following stages:

1. Advance paid
2. Survey done
3. Material ordered
4. Installed
5. Net metering applied
6. Net metering done
7. Subsidy applied
8. Subsidy credited

## Bill image handling

Bill image extraction is an assisted feature. Staff must review extracted fields and confirm them before generating a quotation. If extraction fails or returns incomplete information, the application supports manual entry. Do not treat machine-extracted values as verified until a staff member confirms them.

## Tests

From the repository root:

```bash
source .venv/bin/activate
cd backend
pytest -q
```

## PDF quotation

The current frontend quotation view uses the browser's **Print / Save as PDF** action. In the print dialog, choose **Save as PDF**. Review the generated PDF before sharing it with a customer.

## Security and data handling

- Keep `.env`, database files, uploaded bills, and customer data out of Git.
- Use a unique, high-entropy `SECRET_KEY` in every environment.
- Use HTTPS for deployed environments.
- Use strong, unique staff passwords and rotate any credentials that may have been exposed during development.
- Restrict staff account creation to administrators.
- Keep customer consent and privacy obligations in mind when collecting and processing personal information.
- Do not use demonstration tariff or pricing assumptions for a binding customer quotation.

## Deployment notes

The backend is designed to support PostgreSQL through its database configuration. Before deploying:

1. Provision a PostgreSQL database.
2. Set the production database URL and a strong `SECRET_KEY`.
3. Configure CORS to allow only the deployed frontend origin.
4. Configure persistent storage for uploaded bill images, or move uploads to a private object-storage service.
5. Run `alembic upgrade head` as part of deployment.
6. Set the frontend API base URL to the deployed backend.
7. Verify authentication, bill upload, manual confirmation, quotation generation, project creation, and public status endpoints.
8. Replace all demonstration price and tariff rules with verified, date-effective business data.

The frontend can be deployed as a static Vite build on a static hosting provider. The FastAPI backend can be deployed on a Python application host that supports persistent configuration and the selected database.

## Project status

This repository contains a working development implementation. Before production use, verify deployment configuration, real tariff and pricing data, bill-image storage, customer-facing status-page presentation, and all end-to-end workflows in the target environment.
