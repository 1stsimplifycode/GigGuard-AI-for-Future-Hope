"""
ARIA-Gig / GigGuard — Invisible Loss Insurance Platform
FastAPI Backend Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn

from routers import risk, policy, analytics, admin, payout
from utils.seed_data import seed_database

app = FastAPI(
    title="ARIA-Gig / GigGuard API",
    description="Invisible Loss Insurance for Delivery Partners — Risk Engine & Policy Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk Engine"])
app.include_router(policy.router, prefix="/api/v1/policy", tags=["Policy"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(payout.router, prefix="/api/v1/payout", tags=["Payout"])


@app.on_event("startup")
async def startup_event():
    seed_database()


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "ARIA-Gig GigGuard API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "uptime": "operational"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
