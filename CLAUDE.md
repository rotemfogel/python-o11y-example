# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python web application for user and password management, exposing a REST API backed by PostgreSQL with OpenTelemetry instrumentation.

**Stack:** FastAPI · PostgreSQL · OpenTelemetry

**API operations:** create user, validate authentication, change password, remove users (no GET/query endpoint)

## Database Schema

Single `users` table:

| column      | type         | nullable |
|-------------|--------------|----------|
| id          | serial PK    | No       |
| user_name   | varchar(36)  | No       |
| created_at  | timestamp    | No       |
| updated_at  | timestamp    | No       |
| password    | text         | No       |

## Infrastructure

`docker-compose.yml` brings up the full backing stack:

| Service            | Port(s)       | Purpose                         |
|--------------------|---------------|---------------------------------|
| `postgres`         | 5432          | Application database            |
| `victoria-metrics` | 8428          | Metrics storage (OTLP + PromQL) |
| `victoria-logs`    | 9428          | Log storage (OTLP)              |
| `otel-collector`   | 4317 (gRPC), 4318 (HTTP) | OTLP receiver; fans out to VM and VL |

```bash
docker compose up -d          # start all services
docker compose down -v        # stop and remove volumes
```

The app (once implemented) should set:
- `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`
- `DATABASE_URL=postgresql://app:app@localhost:5432/o11y`

`otel-collector-config.yaml` wires the OTLP receiver to VictoriaMetrics (metrics pipeline) and VictoriaLogs (logs pipeline). Traces go to the `debug` exporter — add a trace backend and update the traces pipeline when needed.

## Development Setup

```bash
pip install -r requirements.txt

# run locally (postgres must be reachable at DATABASE_URL)
uvicorn app.main:app --reload

# apply migration
psql postgresql://app:app@localhost:5432/o11y -f migrations/001_create_users_table.sql

# full stack via Docker
docker compose up --build
```

## Application Structure

```
app/
├── main.py          # FastAPI app creation + OTel wiring
├── telemetry.py     # Traces, metrics, and logs setup (OTLP gRPC)
├── database.py      # SQLAlchemy engine, session factory, Base
├── models.py        # User ORM model
├── schemas.py       # Pydantic request/response models
└── routers/
    └── users.py     # All /users endpoints
migrations/
└── 001_create_users_table.sql   # DDL + updated_at trigger
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/users` | Create user (201, hashes password with bcrypt) |
| `DELETE` | `/users/{user_name}` | Delete user (204) |
| `POST` | `/users/authenticate` | Validate credentials (200 / 401) |
| `PUT` | `/users/{user_name}/password` | Change password (verifies current first) |

## Telemetry

`app/telemetry.py` initialises all three OTel signals at startup and instruments FastAPI and SQLAlchemy automatically:
- **Traces** → OTLP gRPC → collector → `debug` exporter
- **Metrics** → OTLP gRPC → collector → VictoriaMetrics (exported every 10 s)
- **Logs** → OTLP gRPC → collector → VictoriaLogs (Python `logging` bridge)
