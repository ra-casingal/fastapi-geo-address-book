# Address Book API

A RESTful API for managing a geo-aware address book. Supports full CRUD operations on addresses and location-based search to find all addresses within a given radius. Built with **FastAPI**, **SQLAlchemy**, **Pydantic v2**, and **geopy**.

---

## Features

- Create, read, update, and delete addresses
- Find addresses within a given radius using geodesic distance (geopy)
- Input validation with Pydantic v2 (coordinate range constraints)
- SQLite database via SQLAlchemy 2.x ORM
- Configuration fully driven by environment variables via pydantic-settings
- Structured logging and consistent error handling throughout

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
├── .env                           # Local environment variables (git-ignored)
├── .env.example                   # Template — safe to commit
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/ra-casingal/fastapi-geo-address-book.git
cd fastapi-geo-address-book
```

### 2. Create a virtual environment

```bash
# Windows
py -3 -m venv venv

# macOS / Linux
python3 -m venv venv
```

### 3. Activate the virtual environment

```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.\venv\Scripts\activate.bat

# macOS / Linux
source venv/bin/activate
```

> **Windows note:** if PowerShell blocks script execution, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create the `.env` file

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

### 6. Run the server

```bash
uvicorn app.main:app --reload
```

---

## Environment Variables

All configuration is loaded from `.env` (copy from `.env.example`). No values are hardcoded in source code.

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
| `LOG_LEVEL`    | `INFO`                        | Logging verbosity: DEBUG, INFO, WARNING, ERROR |

---

## Running the Application

```bash
uvicorn app.main:app --reload
```

| URL                           | Description            |
|-------------------------------|------------------------|
| `http://127.0.0.1:8000/docs`  | Interactive Swagger UI |
| `http://127.0.0.1:8000/redoc` | ReDoc documentation    |

---

## API Endpoints

All endpoints are prefixed with `/api/v1`.

| Method   | Endpoint            | Description                                 |
|----------|---------------------|---------------------------------------------|
| `POST`   | `/addresses`        | Create a new address                        |
| `GET`    | `/addresses`        | List all addresses (supports pagination)    |
| `GET`    | `/addresses/{id}`   | Retrieve a single address by ID             |
| `PUT`    | `/addresses/{id}`   | Update an existing address (partial update) |
| `DELETE` | `/addresses/{id}`   | Delete an address by ID                     |
| `GET`    | `/addresses/nearby` | Find addresses within a given radius (km)   |

### Query parameters

**`GET /api/v1/addresses`**
- `skip` (int, default `0`) — number of records to skip
- `limit` (int, default `100`) — maximum records to return

**`GET /api/v1/addresses/nearby`**
- `latitude` (float, required) — origin latitude in decimal degrees
- `longitude` (float, required) — origin longitude in decimal degrees
- `radius_km` (float, required) — search radius in kilometres

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
  "created_at": "2026-03-20T10:00:00",
  "updated_at": "2026-03-20T10:00:00"
}
```

### Find nearby addresses

```bash
curl "http://127.0.0.1:8000/api/v1/addresses/nearby?latitude=51.5074&longitude=-0.1278&radius_km=500"
```

Returns all addresses stored within 500 km of the given coordinates.

---

## Notes & Assumptions

- **SQLite** is used as the database for simplicity and zero-config local setup. The `DATABASE_URL` environment variable can be changed to PostgreSQL or MySQL without any code changes.
- **No authentication** is implemented — this is intentional for assessment scope.
- **Swagger UI** (`/docs`) serves as the interactive API client; no separate GUI is required.
- **Geospatial distance** is calculated using `geopy.distance.geodesic`, which uses the WGS-84 ellipsoid for accuracy. Filtering is performed in application memory, which is appropriate for SQLite at assessment scale.
- Coordinates are validated at the schema level: latitude must be in `[-90, 90]` and longitude in `[-180, 180]`.
