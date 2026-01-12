# CredoCarbon SuperAdmin Backend

FastAPI backend for managing registry data in the CredoCarbon website.

## Quick Start

```bash
# Navigate to the backend directory
cd backend

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login with username/password |
| GET | `/api/auth/me` | Get current user info |
| POST | `/api/auth/verify` | Verify token validity |

### Registries (Requires Authentication)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/registries/all` | Get all registry data |
| GET | `/api/registries/carbon` | Get all carbon registries |
| GET | `/api/registries/rec` | Get all REC registries |
| GET | `/api/registries/ets` | Get all ETS registries |
| GET | `/api/registries/{type}/{id}` | Get specific registry |
| POST | `/api/registries/{type}` | Create new registry |
| PUT | `/api/registries/{type}/{id}` | Update registry |
| DELETE | `/api/registries/{type}/{id}` | Delete registry |

### API Documentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Default Credentials

**Username:** `superadmin`  
**Password:** `CredoCarbon@2025`

> ⚠️ **Important:** Change these credentials in production by setting environment variables:
> - `ADMIN_USERNAME`
> - `ADMIN_PASSWORD`
> - `SECRET_KEY`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | `credocarbon-superadmin-secret-key-change-in-production` |
| `ADMIN_USERNAME` | Admin username | `superadmin` |
| `ADMIN_PASSWORD` | Admin password | `CredoCarbon@2025` |

## Data Files

The backend reads and writes to these JSON files in `/public/Data/`:
- `registryData.json` - Main registry data for the banner and Registries page
- `insightsData.json` - Detailed insights data with sector breakdowns

## Frontend Access

Access the SuperAdmin panel at: **http://localhost:5173/superadmin**

## Architecture

```
backend/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration settings
├── auth.py              # JWT authentication utilities
├── models.py            # Pydantic data models
├── utils.py             # File I/O utilities
├── requirements.txt     # Python dependencies
└── routes/
    ├── __init__.py
    ├── auth_routes.py   # Login/auth endpoints
    └── registry_routes.py # CRUD endpoints
```

## CORS Configuration

Allowed origins are configured in `config.py`. Add your production domain there.

## Running in Production

1. Use a proper WSGI/ASGI server (e.g., Gunicorn with uvicorn workers)
2. Set strong SECRET_KEY via environment variable
3. Update CORS origins for your domain
4. Store admin credentials securely (use database instead of hardcoded)
5. Use HTTPS

```bash
# Production example
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

