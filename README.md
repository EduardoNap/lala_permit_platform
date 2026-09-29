# LALA Permit Management Platform

A full-stack web platform for tracking **environmental and government permits** across a network of distribution centers grouped by region. Users upload permit PDFs, and an **AWS Textract + Amazon Bedrock** pipeline reads the document and pre-fills the permit's key fields (issuing authority, registration number, issue date, expiry date, and conditions). Compliance status, expiry risk, and pending conditions are shown on a dashboard.

Built in Python with Reflex, backed by PostgreSQL, and deployed on AWS with Docker.

---

## Features

- **Compliance dashboard**: KPIs, expiry trends, and at-risk CEDIS at a glance.
- **Region → CEDIS navigation**: drill down from a region to each distribution center and its permits; edit CEDIS details.
- **AI-assisted permit upload**: a guided flow for uploading the acknowledgment receipt, proof of payment, permit, and extra documents. PDFs are stored in S3, OCR'd with Textract, and parsed by an LLM on Bedrock into structured fields. Every extracted field includes the literal OCR text it came from.
- **Automatic permit status** based on the expiry date:
  - `Ingresado`: registered, primary PDF not uploaded yet
  - `Vigente`: valid, more than 90 days remaining
  - `Por vencer`: expires within 90 days
  - `Vencido`: expired
- **Conditions tracking** (*condicionantes*): each permit's obligations as a task list with progress bars.
- **Audit history**: previous versions of each permit, their associated PDFs, and status changes, filterable by owner and zone.
- **Email notifications** via Amazon SES when a permit is uploaded.
- **Authentication**: user accounts with PBKDF2-HMAC-SHA256 password hashing (salted, 120k iterations).

## Architecture

```
            ┌──────────────────────────────┐
 Browser ──▶│  Reflex app (Python)         │
 (React UI) │  frontend :3000 / API :8000  │
            └──┬─────────┬─────────┬───────┘
               │         │         │
      SQLAlchemy│    boto3│         │boto3
               ▼         ▼         ▼
        ┌──────────┐ ┌───────┐ ┌──────────┐
        │PostgreSQL│ │  S3   │ │   SES    │
        │ permits, │ │ PDFs  │ │  email   │
        │ users,   │ └───┬───┘ └──────────┘
        │ history  │     │
        └──────────┘     ▼
                   ┌──────────┐   OCR text   ┌──────────────┐
                   │ Textract │─────────────▶│   Bedrock    │
                   │ (async)  │              │ LLM → JSON   │
                   └──────────┘              │ (Pydantic)   │
                                             └──────────────┘
```

**Upload data flow:** PDF upload → S3 → asynchronous Textract job (polled with backoff) → text lines → Bedrock prompt → JSON validated against a Pydantic schema (`GovFields`) → dates normalized → form pre-filled for the user to review → saved to PostgreSQL → SES notification.

**Data model:** `Zone` → `Cedis` → `Permit` → `PermitPdf` / `PermitCondition` / `PermitStatusHistory`. `User` is linked to `Permit` and `Notification`.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend + backend | Reflex 0.8 (Python → React), Radix UI, TailwindCSS v4 |
| Database | PostgreSQL, SQLAlchemy 2.0 |
| Document AI | AWS Textract (async OCR), Amazon Bedrock (LLM extraction), Pydantic |
| Storage / email | Amazon S3, Amazon SES |
| PDF processing | PyMuPDF, Docling |
| Deployment | Docker |

## Project structure

```
prueba/
├── prueba.py           # App entry point, page routing
├── state.py            # Reflex State: event handlers & app logic
├── db.py / db_models.py# DB setup, seeding, SQLAlchemy models
├── pdf_extraction.py   # Textract OCR + Bedrock LLM field extraction
├── storage.py          # S3 upload / presigned URLs
├── notifications.py    # SES email notifications
├── auth.py             # Password hashing & verification
├── pages/              # dashboard, regiones, cedis, cargar-permiso, tareas, historial, login, acerca
└── components/         # sidebar, header, KPI cards, panels, CEDIS dashboard
```

## Running locally

**Requirements:** Python 3.11, Node.js, a PostgreSQL database, and an AWS account with access to S3, Textract, Bedrock, and SES.

```bash
git clone <this-repo>
cd lala-permit-platform
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # fill in your own values
set -a && source .env && set +a

reflex run                # http://localhost:3000
```

On first startup the app creates the tables and seeds the regions and CEDIS. The login page then lets you create the first admin user.

> `rxconfig.py` sets `api_url` to the original deployment domain. For local development, remove it or change it to `http://localhost:8000`.

### Docker

```bash
docker build -t lala-permit-platform .
docker run --env-file .env -p 3000:3000 -p 8000:8000 lala-permit-platform
```

## Author

- Eduardo García
