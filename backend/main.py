"""
ARIA-Gig / GigGuard — Invisible Loss Insurance for Delivery Partners
FastAPI Backend — Production Entry Point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from routers import risk, insurance, admin, analytics, partners
from core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ARIA-Gig API",
    description="Invisible Loss Insurance Platform for Delivery Partners",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(risk.router,       prefix="/api/v1/risk",      tags=["Risk Engine"])
app.include_router(insurance.router,  prefix="/api/v1/insurance",  tags=["Insurance"])
app.include_router(admin.router,      prefix="/api/v1/admin",      tags=["Admin"])
app.include_router(analytics.router,  prefix="/api/v1/analytics",  tags=["Analytics"])
app.include_router(partners.router,   prefix="/api/v1/partners",   tags=["Partners"])


@app.get("/", tags=["Health"])
async def root():
    return {"service": "ARIA-Gig API", "version": "1.0.0", "status": "operational"}


@app.get("/api/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "service": "aria-gig-backend",
        "version": "1.0.0",
    }


@app.exception_handler(404)
async def not_found(request, exc):
    return JSONResponse(status_code=404, content={"error": "Route not found"})


@app.exception_handler(500)
async def server_error(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
