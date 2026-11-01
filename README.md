# Complyance CRM ↔ Zoho Books Integration

A FastAPI-based integration that synchronizes CRM Closed Won deals with Zoho Books.

## Architecture

CRM
  ↓
FastAPI Integration Layer
  ↓
PostgreSQL
  ↓
Zoho Books API

The integration layer stores CRM and Zoho external IDs and maintains
the relationship between deals, sales orders, invoices and payments.

## Implemented

- CRM Closed Won deal processing
- Zoho OAuth refresh-token authentication
- Zoho customer lookup/create
- Customer duplicate prevention
- Sales Order creation
- 3 milestone invoices
- 50% / 30% / 20% milestone allocation
- PostgreSQL persistence
- Deal-level idempotency
- Decimal-based monetary calculations
- FastAPI REST API
- Swagger/OpenAPI documentation

## Example

Deal amount:

₹120,000

Milestone invoices:

- Signing — 50% — ₹60,000
- Go-live — 30% — ₹36,000
- 90 days after go-live — 20% — ₹24,000

Total:

₹120,000

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- HTTPX
- Zoho Books API
- Pytest

## Database

The database stores:

- Customers
- Deals
- Sales Orders
- Invoices
- Payments
- Integration Events
- Integration Logs
- Sync State

External CRM and Zoho IDs are persisted for traceability.

## Idempotency

Before processing a Closed Won deal, the integration checks whether
a Sales Order already exists for the deal.

Repeated processing therefore returns the existing Sales Order instead
of creating another one.

## Security

Credentials are stored in environment variables.

`.env` is excluded from Git and secrets are never committed to the
repository.

## Running Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload