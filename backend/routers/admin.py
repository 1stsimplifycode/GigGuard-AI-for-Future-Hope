"""Admin Router"""
from fastapi import APIRouter
from core.insurance_engine import insurance_engine
import random
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard")
async def admin_dashboard():
    pool = insurance_engine.get_pool_summary()
    # Simulate 30-day trend
    weekly = []
    for i in range(8):
        premiums = random.randint(45000, 75000)
        payouts = random.randint(10000, 40000)
        weekly.append({
            "week": f"W{i+1}",
            "premiums_collected": premiums,
            "payouts_processed": payouts,
            "net": premiums - payouts,
        })
    return {
        "pool": pool,
        "weekly_trend": weekly,
        "trigger_stats": {
            "weather_triggers": random.randint(120, 280),
            "aqi_triggers": random.randint(80, 150),
            "demand_triggers": random.randint(200, 400),
            "fuel_triggers": random.randint(60, 120),
        },
        "payout_tier_distribution": {
            "T1": random.randint(40, 80),
            "T2": random.randint(30, 60),
            "T3": random.randint(20, 40),
            "T4": random.randint(5, 20),
        },
    }
