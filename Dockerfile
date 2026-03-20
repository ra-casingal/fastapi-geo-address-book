# syntax=docker/dockerfile:1

# ── Base image ─────────────────────────────────────────────────────────────
# python:3.13-slim keeps the image small while remaining fully compatible
# with all project dependencies.
FROM python:3.13-slim

# ── System hardening ────────────────────────────────────────────────────────
# Disable .pyc files and enable unbuffered stdout/stderr (better for logs).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── Working directory ────────────────────────────────────────────────────────
WORKDIR /app

# ── Dependencies ─────────────────────────────────────────────────────────────
# Copy only the requirements file first so Docker can cache this layer;
# it is only invalidated when requirements.txt actually changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ──────────────────────────────────────────────────────────
COPY app/ ./app/
COPY tests/ ./tests/

# ── SQLite data directory ─────────────────────────────────────────────────────
# Create the directory that will hold the SQLite database file.
# docker-compose mounts ./data here so the file survives container restarts.
RUN mkdir -p /app/data

# ── Network ───────────────────────────────────────────────────────────────────
EXPOSE 8000

# ── Startup ───────────────────────────────────────────────────────────────────
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
