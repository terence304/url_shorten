# URL Shortener

A high-performance URL shortener built with FastAPI, PostgreSQL, and Redis.

## Features

- **Shorten URLs** with auto-generated base62 keys or custom aliases
- **Fast redirects** via Redis cache with PostgreSQL fallback
- **User accounts** with JWT authentication
- **Click analytics** -- total clicks, referrers, countries, time-series
- **Soft-delete** and URL expiration support

## Architecture

```
Client -> FastAPI -> Redis (cache: key -> long_url)
                  -> PostgreSQL (persistence + analytics)
```

- **Key generation**: Base62 encoding of auto-increment ID
- **Capacity**: 7-char key = 3.5 trillion URLs (100M/day for 96 years)

## Quick Start

### 1. Start infrastructure

```bash
docker-compose up -d
```

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 3. Run database migrations

```bash
alembic upgrade head
```

### 4. Start the server

```bash
uvicorn app.main:app --reload
```

### 5. Try it out

```bash
# Shorten a URL
curl -X POST http://localhost:8000/api/v1/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://example.com/very/long/path"}'

# Follow the short URL
curl -L http://localhost:8000/<short_key>
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/shorten` | Optional | Create short URL |
| GET | `/{short_key}` | No | Redirect to long URL |
| POST | `/api/v1/auth/register` | No | Create account |
| POST | `/api/v1/auth/login` | No | Get JWT token |
| GET | `/api/v1/urls` | Required | List your URLs |
| DELETE | `/api/v1/urls/{key}` | Required | Deactivate a URL |
| GET | `/api/v1/urls/{key}/stats` | Required | Click analytics |
| GET | `/health` | No | Health check |

## Running Tests

```bash
pip install -e ".[dev]"
pytest -v
```

## Project Structure

```
app/
  main.py           # FastAPI app + lifespan
  config.py         # Env-based settings
  base62.py         # Key encoding
  models.py         # SQLAlchemy ORM models
  schemas.py        # Pydantic request/response
  database.py       # Async DB engine
  redis_client.py   # Redis wrapper
  deps.py           # Auth dependencies
  routers/          # API route handlers
  services/         # Business logic
tests/              # pytest test suite
```

## Configuration

All settings via environment variables (or `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `BASE_URL` | `http://localhost:8000` | Public base URL |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT lifetime |

## Usage
```bash
cd ~/nemo/url_shorten
docker-compose up -d        # Start PostgreSQL + Redis
source venv/bin/activate
alembic upgrade head        # Create tables
uvicorn app.main:app --reload
docker-compose down         # Stop services when done
```