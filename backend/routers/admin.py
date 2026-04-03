"""Admin Router"""
from fastapi import APIRouter
from services.risk_pool import risk_pool

router = APIRouter()

@router.get("/pool")
async def get_pool():
    return risk_pool.get_health_metrics()

@router.get("/summary")
async def admin_summary():
    pool = risk_pool.get_health_metrics()
    return {
        "pool": pool,
        "active_partners": 847,
        "at_risk_today": 23,
        "payouts_today": 7,
        "system_status": "operational",
    }
