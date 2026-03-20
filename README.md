# Address Book API

A geo-aware RESTful address book built with **FastAPI**, **SQLAlchemy**, and **SQLite**. Designed as a clean, minimal, production-ready Python microservice.

---

## Features

- **FastAPI** — high-performance ASGI framework with automatic OpenAPI docs
- **SQLAlchemy 2.x ORM** — type-safe database access with a declarative model layer
- **SQLite** (default) — zero-config local database; swappable for PostgreSQL or MySQL via `DATABASE_URL`
- **Pydantic v2 + pydantic-settings** — validated settings loaded from environment variables
- **geopy** — geospatial distance calculations between addresses
- **python-dotenv** — `.env` file support for local development

---

## Requirements

- Python **3.10+** (tested on 3.14)
- `pip` or any PEP 517-compatible package manager

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/fastapi-geo-address-book.git
cd fastapi-geo-address-book
```

### 2. Create and activate a virtual environment

```bash
# Windows (PowerShell)
py -3.14 -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

> **Windows note:** if script execution is blocked, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` if you need to change the database URL or any other setting. See [Environment Variables](#environment-variables) below for the full reference.

### 5. Run the development server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000` | Root health-check endpoint |
| `http://127.0.0.1:8000/docs` | Interactive Swagger UI |
| `http://127.0.0.1:8000/redoc` | ReDoc documentation |

---

## Environment Variables

All variables are read from `.env` in the project root (copy from `.env.example`).

| Variable | Required | Default | Description |
|---|---|---|---|
| `PROJECT_NAME` | No | `"Address Book API"` | Name shown in the OpenAPI `/docs` UI |
| `VERSION` | No | `"0.1.0"` | Semantic version returned by `GET /` |
| `DATABASE_URL` | No | `sqlite:///./address_book.db` | SQLAlchemy connection string (see examples below) |

### `DATABASE_URL` examples

```dotenv
# SQLite — default, no extra dependencies needed
DATABASE_URL="sqlite:///./address_book.db"

# PostgreSQL — install psycopg2-binary first
DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/address_book"

# MySQL / MariaDB — install PyMySQL first
DATABASE_URL="mysql+pymysql://user:password@localhost:3306/address_book"
```

---

## Project Structure

```
fastapi-geo-address-book/
├── app/
│   ├── main.py              # FastAPI app factory, startup hooks, root route
│   │
│   ├── api/                 # Route modules (APIRouter instances)
│   │   └── __init__.py
│   │
│   ├── models/              # SQLAlchemy ORM model classes (inherit from Base)
│   │   └── __init__.py
│   │
│   ├── schemas/             # Pydantic request/response schemas
│   │   └── __init__.py
│   │
│   ├── services/            # Business logic (e.g. geopy distance calculations)
│   │   └── __init__.py
│   │
│   ├── db/
│   │   ├── base.py          # Declarative Base — all models register here
│   │   ├── session.py       # Engine + SessionLocal factory
│   │   └── deps.py          # get_db() FastAPI dependency
│   │
│   └── core/
│       └── config.py        # Pydantic-settings Settings class
│
├── .env                     # Local secrets (git-ignored)
├── .env.example             # Template — commit this, not .env
├── .gitignore
└── requirements.txt
```

### Layer responsibilities

| Directory | Responsibility |
|---|---|
| `api/` | HTTP layer — declare routes, validate HTTP concerns, call services |
| `models/` | Database layer — ORM table definitions |
| `schemas/` | Contract layer — Pydantic models for request bodies and responses |
| `services/` | Business layer — logic that is independent of HTTP and database details |
| `db/` | Infrastructure layer — engine, session lifecycle, DI wiring |
| `core/` | Cross-cutting — settings, shared constants |

---

## Running in Production

Replace `--reload` (development-only) with explicit worker configuration:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Or use **Gunicorn** with the Uvicorn worker class:

```bash
pip install gunicorn
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8000
```

---

## License

MIT
