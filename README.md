# Breathe ESG Tech Assignment

A Django REST Framework prototype for ingesting enterprise ESG activity data, normalizing it into emissions entries, and supporting analyst review with auditability.

The project focuses on three realistic source systems:

- SAP fuel/procurement exports for Scope 1 fuel emissions
- Utility electricity CSVs for Scope 2 purchased electricity
- Corporate travel exports for Scope 3 business travel emissions

## Live Deployment

- **Frontend:** https://breathe-esg-frontend-sigma.vercel.app
- **Backend API:** https://breatheesgtechassignment-production.up.railway.app

## Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@acme.com | acmeadmin123 |
| Analyst | analyst@acme.com | acmeanalyst123 |

## What This Builds

This prototype supports:

- Multi-tenant data isolation through a custom `Tenant` model and tenant-scoped query access
- CSV upload and ingestion by source type
- Raw row preservation for traceability
- Source-specific parsing and normalization
- Emissions calculation using stored emission factors
- Review workflow for pending, flagged, approved, and rejected entries
- Locked approved records
- Audit logs with before/after state snapshots
- Sample data seeding through a Django management command

## Tech Stack

**Backend**
- Python, Django 4.2, Django REST Framework 3.15
- PostgreSQL (Railway)
- django-cors-headers, python-dotenv, gunicorn, dj-database-url

**Frontend**
- React 19, Vite
- Tailwind CSS, Recharts, Tanstack React Query
- Deployed on Vercel

## Repository Structure

```text
.
├── breathe_esg/          # Django project and apps
├── frontend/             # React frontend
├── MODEL.md              # Data model and rationale
├── DECISIONS.md          # Ambiguities and design choices
├── TRADEOFFS.md          # Deliberate omissions and next steps
├── SOURCES.md            # Source-system research and sample data rationale
└── Breathe_ESG_Tech_Intern_Assignment.pdf
```

## Local Setup

**Backend:**

```bash
cd breathe_esg
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Update `.env` with your PostgreSQL credentials:

```env
DB_NAME=breathe_esg
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

Then run:

```bash
python manage.py migrate
python manage.py seed_sample_data
python manage.py runserver
```

**Frontend:**

```bash
cd frontend
npm install --legacy-peer-deps
cp .env.example .env
# Set VITE_API_URL=http://127.0.0.1:8000 in .env
npm run dev
```

## Sample Data

`seed_sample_data` ingests three CSV files through the normal parser/normalizer pipeline:

- `sap_sample.csv` — 10 rows of SAP fuel/procurement data (9 valid, 1 error)
- `utility_sample.csv` — 8 rows of utility electricity data (7 valid, 1 error)
- `travel_sample.csv` — 12 rows of corporate travel data (9 valid, 3 errors)

## API Overview

**Authentication:**
- `POST /api/auth/login/`

**Ingestion:**
- `POST /api/ingest/upload/`
- `GET /api/ingest/batches/`
- `GET /api/ingest/batches/<batch_id>/`

**Review:**
- `GET /api/review/dashboard/`
- `GET /api/review/entries/`
- `GET /api/review/entries/<entry_id>/`
- `PATCH /api/review/entries/<entry_id>/`
- `POST /api/review/entries/<entry_id>/action/`
- `GET /api/review/audit/`

## Design Notes

The implementation intentionally keeps source integrations file-based rather than API-based. That mirrors a realistic first-client onboarding flow where sustainability, facilities, finance, or travel teams export CSVs from existing systems before direct integrations are available.

For deeper rationale, see:

- [`MODEL.md`](./MODEL.md) — Data model, multi-tenancy, audit trail
- [`DECISIONS.md`](./DECISIONS.md) — Every ambiguity resolved with reasoning
- [`TRADEOFFS.md`](./TRADEOFFS.md) — What was deliberately not built and why
- [`SOURCES.md`](./SOURCES.md) — Real-world source research and sample data rationale