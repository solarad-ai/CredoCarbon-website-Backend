"""
CredoCarbon SuperAdmin API

FastAPI backend for managing registry data.
Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS
from routes.auth_routes import router as auth_router
from routes.registry_routes import router as registry_router
from routes.insights_routes import router as insights_router

# Create FastAPI app
app = FastAPI(
    title="CredoCarbon SuperAdmin API",
    description="Backend API for managing carbon registry data",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(registry_router)
app.include_router(insights_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "CredoCarbon SuperAdmin API",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """API health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
