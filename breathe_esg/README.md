# Breathe ESG

Django REST Framework prototype for tenant-scoped ESG data ingestion, normalization, review, and audit trails.

## Setup

```bash
cd breathe_esg
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Update `.env` with PostgreSQL credentials:

```env
DB_NAME=breathe_esg
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

## Run Locally

```bash
python manage.py migrate
python manage.py runserver
```

## Seed Data

```bash
python manage.py seed_sample_data
```

This creates tenant `Acme Corp`, users `admin@acme.com` / `analyst@acme.com`, writes three CSVs into `sample_data/`, and ingests them through the parser and normalizer pipeline.

## API Endpoints

- `POST /api/auth/login/`
- `POST /api/ingest/upload/`
- `GET /api/ingest/batches/`
- `GET /api/ingest/batches/<batch_id>/`
- `GET /api/review/dashboard/`
- `GET /api/review/entries/`
- `GET /api/review/entries/<entry_id>/`
- `PATCH /api/review/entries/<entry_id>/`
- `POST /api/review/entries/<entry_id>/action/`
- `GET /api/review/audit/`

## Sample Credentials

- Admin: `admin@acme.com` / `acmeadmin123`
- Analyst: `analyst@acme.com` / `acmeanalyst123`
