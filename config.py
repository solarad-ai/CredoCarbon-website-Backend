import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Security - loaded from .env file (not committed to git)
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Admin credentials - loaded from .env file (not committed to git)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")

# Paths (for local development fallback)
BACKEND_DIR = Path(__file__).parent
PROJECT_ROOT = BACKEND_DIR.parent
PUBLIC_DATA_DIR = PROJECT_ROOT / "public" / "Data"

# Google Cloud Storage Configuration
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "credocarbon-metadata")
GCS_INSIGHTS_FILE = os.getenv("GCS_INSIGHTS_FILE", "insightsData.json")
GCS_REGISTRY_FILE = os.getenv("GCS_REGISTRY_FILE", "registryData.json")

# If True, use GCS. If False, use local files (for development)
USE_GCS = os.getenv("USE_GCS", "true").lower() == "true"

# CORS
CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "")
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "https://credocarbon.com",
    "https://www.credocarbon.com",
    "https://credocarbon.netlify.app"
]

# Add any additional origins from environment variable
if CORS_ORIGINS_ENV:
    additional_origins = [origin.strip() for origin in CORS_ORIGINS_ENV.split(",")]
    ALLOWED_ORIGINS.extend(additional_origins)
