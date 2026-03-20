# Address Book API

A RESTful API for managing a geo-aware address book. Supports full CRUD operations on addresses and location-based search to find all addresses within a given radius. Built with **FastAPI**, **SQLAlchemy**, **Pydantic v2**, and **geopy**. Fully containerised with Docker.

---

## Features

- Create, read, update, and delete addresses
- Find addresses within a given radius using geodesic distance (geopy)
- Input validation with Pydantic v2 (coordinate range constraints)
- SQLite persistence via SQLAlchemy 2.x ORM
- Configuration driven by environment variables via pydantic-settings
- Structured logging and consistent error handling
- Interactive API via Swagger UI (`/docs`) — no separate client required
- Automated test suite with pytest (schema, service, route, and end-to-end flow)
- Dockerised with Docker Compose for zero-config container deployment

---

## Project Structure

```
fastapi-geo-address-book/
├── app/
│   ├── main.py                    # App factory, startup, global exception handlers
│   ├── api/
│   │   └── routes/
│   │       └── address.py         # All address endpoints (APIRouter)
│   ├── models/
│   │   └── address.py             # SQLAlchemy ORM model
│   ├── schemas/
│   │   └── address.py             # Pydantic request/response schemas
│   ├── services/
│   │   └── address_service.py     # CRUD + geospatial business logic
│   ├── db/
│   │   ├── base.py                # Declarative Base
│   │   ├── session.py             # Engine + SessionLocal factory
│   │   └── deps.py                # get_db() FastAPI dependency
│   └── core/
│       ├── config.py              # Settings (pydantic-settings)
│       └── logger.py              # Logging configuration
├── tests/
│   ├── conftest.py                # Fixtures: in-memory DB, TestClient, dependency override
│   ├── test_schemas.py            # Pydantic validation tests
│   ├── test_services.py           # Service layer tests
│   ├── test_routes.py             # HTTP endpoint tests
│   └── test_api_flow.py           # End-to-end API flow test
├── scripts/
│   └── check_dependencies.py      # Audits requirements.txt against actual imports
├── Dockerfile
├── docker-compose.yml
├── .env                           # Local environment variables (git-ignored)
├── .env.example                   # Template — safe to commit
├── requirements.txt
└── README.md
```

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/ra-casingal/fastapi-geo-address-book.git
cd fastapi-geo-address-book
```

### 2. Create and activate a virtual environment

```bash
# Windows
py -3 -m venv venv
.\venv\Scripts\Activate.ps1      # PowerShell
# .\venv\Scripts\activate.bat    # Command Prompt

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

> **Windows PowerShell note:** if script execution is blocked, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.
Interactive Swagger UI: `http://127.0.0.1:8000/docs`

---

## Environment Variables

All configuration is loaded from `.env`. No values are hardcoded in source.

```dotenv
PROJECT_NAME="Address Book API"
VERSION="0.1.0"
DATABASE_URL="sqlite:///./address_book.db"
LOG_LEVEL="INFO"
```

| Variable       | Default                       | Description                                    |
|----------------|-------------------------------|------------------------------------------------|
| `PROJECT_NAME` | `Address Book API`            | Name displayed in the OpenAPI docs UI          |
| `VERSION`      | `0.1.0`                       | API version string                             |
| `DATABASE_URL` | `sqlite:///./address_book.db` | SQLAlchemy connection string                   |
| `LOG_LEVEL`    | `INFO`                        | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

> **Docker note:** `docker-compose.yml` overrides `DATABASE_URL` to
> `sqlite:////app/data/address_book.db` so the database is written to the
> mounted volume (`./data`) and survives container restarts. Your `.env` stays
> unchanged for local development.

---

## API Endpoints

All endpoints are prefixed with `/api/v1`.

| Method   | Path                        | Description                                    |
|----------|-----------------------------|------------------------------------------------|
| `POST`   | `/addresses`                | Create a new address                           |
| `GET`    | `/addresses`                | List all addresses                             |
| `GET`    | `/addresses/{id}`           | Retrieve a single address by ID                |
| `PUT`    | `/addresses/{id}`           | Partially update an address                    |
| `DELETE` | `/addresses/{id}`           | Delete an address by ID                        |
| `GET`    | `/addresses/nearby`         | Find addresses within a given radius (km)      |

### Query parameters

**`GET /api/v1/addresses`**
- `skip` (int, default `0`) — records to skip
- `limit` (int, default `100`) — maximum records to return

**`GET /api/v1/addresses/nearby`**
- `latitude` (float, required) — origin latitude in decimal degrees
- `longitude` (float, required) — origin longitude in decimal degrees
- `distance_km` (float, required) — search radius in kilometres

---

## Example Requests

### Create an address

```bash
curl -X POST http://127.0.0.1:8000/api/v1/addresses \
  -H "Content-Type: application/json" \
  -d '{"latitude": 51.5074, "longitude": -0.1278, "name": "London"}'
```

```json
{
  "id": 1,
  "name": "London",
  "latitude": 51.5074,
  "longitude": -0.1278,
  "created_at": "2026-03-21T10:00:00",
  "updated_at": "2026-03-21T10:00:00"
}
```

### Find nearby addresses

```bash
curl "http://127.0.0.1:8000/api/v1/addresses/nearby?latitude=51.5074&longitude=-0.1278&distance_km=500"
```

Returns all stored addresses within 500 km of the given coordinates.

---

## Running Tests

Tests use **pytest** with an isolated in-memory SQLite database. No `.env` changes are required.

```bash
# Run all tests
pytest tests/

# Verbose output
pytest tests/ -v

# End-to-end flow test only
pytest tests/test_api_flow.py -v
```

### Test coverage areas

| File                  | What it tests                                                      |
|-----------------------|--------------------------------------------------------------------|
| `test_schemas.py`     | Pydantic validation — coordinates, field lengths, optional fields  |
| `test_services.py`    | Service layer — CRUD operations and geospatial distance filtering  |
| `test_routes.py`      | HTTP layer — status codes, request/response bodies, edge cases     |
| `test_api_flow.py`    | End-to-end lifecycle: create → read → update → nearby → delete     |

---

## Docker

### Start the API

```bash
docker compose up --build
```

The API is available at `http://localhost:8000` and Swagger UI at `http://localhost:8000/docs`.

### Run in detached mode

```bash
docker compose up --build -d
```

### Stop containers

```bash
docker compose down
```

### Run tests inside the container

```bash
docker compose run --rm --no-deps api python -m pytest tests/ -v
```

### SQLite persistence

The `docker-compose.yml` mounts `./data` on the host to `/app/data` inside the
container. The database file is written there and survives `docker compose down`
and subsequent restarts. The `data/` directory is git-ignored.

---

## Notes & Assumptions

- **SQLite** is used for simplicity and zero-config setup. Swapping to PostgreSQL or MySQL requires only a `DATABASE_URL` change — no code changes.
- **No authentication** is implemented — intentionally out of scope for this assessment.
- **Swagger UI** (`/docs`) is the intended API client; no separate GUI is needed.
- **Geospatial distance** is calculated with `geopy.distance.geodesic` (WGS-84 ellipsoid). Filtering runs in application memory, which is appropriate at SQLite/assessment scale.
- Coordinate validation is enforced at the schema level: latitude `[-90, 90]`, longitude `[-180, 180]`.
- The project is intentionally minimal but structured with clear separation of concerns (routes → services → models).
