# Breathe ESG Tech Assignment

A Django REST Framework prototype for ingesting enterprise ESG activity data, normalizing it into emissions entries, and supporting analyst review with auditability.

The project focuses on three realistic source systems:

- SAP fuel/procurement exports for Scope 1 fuel emissions
- Utility electricity CSVs for Scope 2 purchased electricity
- Corporate travel exports for Scope 3 business travel emissions

The backend is implemented in [`breathe_esg/`](./breathe_esg).

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

- Python
- Django 4.2
- Django REST Framework 3.15
- PostgreSQL
- django-cors-headers
- python-dotenv
- gunicorn

## Repository Structure

```text
.
├── breathe_esg/          # Django project and apps
├── DECISIONS.md          # Ambiguities and design choices
├── MODEL.md              # Data model and rationale
├── SOURCES.md            # Source-system research and sample data rationale
├── TRADEOFFS.md          # Deliberate omissions and next steps
└── Breathe_ESG_Tech_Intern_Assignment.pdf
```

## Local Setup

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

## Sample Users

Created by `seed_sample_data`:

- Admin: `admin@acme.com` / `acmeadmin123`
- Analyst: `analyst@acme.com` / `acmeanalyst123`

## API Overview

Authentication:

- `POST /api/auth/login/`

Ingestion:

- `POST /api/ingest/upload/`
- `GET /api/ingest/batches/`
- `GET /api/ingest/batches/<batch_id>/`

Review:

- `GET /api/review/dashboard/`
- `GET /api/review/entries/`
- `GET /api/review/entries/<entry_id>/`
- `PATCH /api/review/entries/<entry_id>/`
- `POST /api/review/entries/<entry_id>/action/`
- `GET /api/review/audit/`

## Design Notes

The implementation intentionally keeps source integrations file-based rather than API-based. That mirrors a realistic first-client onboarding flow where sustainability, facilities, finance, or travel teams export CSVs from existing systems before direct integrations are available.

For deeper rationale, see:

- [`MODEL.md`](./MODEL.md)
- [`DECISIONS.md`](./DECISIONS.md)
- [`SOURCES.md`](./SOURCES.md)
- [`TRADEOFFS.md`](./TRADEOFFS.md)

