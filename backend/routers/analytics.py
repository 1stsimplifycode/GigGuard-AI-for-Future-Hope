"""Analytics Router"""
from fastapi import APIRouter
from datetime import datetime, timedelta
import random, numpy as np

router = APIRouter()

@router.get("/dashboard")
async def dashboard_analytics():
    """Historical analytics for admin dashboard"""
    weeks = []
    pool = 125000
    for i in range(12):
        premiums = random.randint(8000, 15000)
        payouts = random.randint(3000, 10000)
        pool += premiums - payouts
        weeks.append({
            "week": f"W{i+1}",
            "premiums": premiums,
            "payouts": payouts,
            "net": premiums - payouts,
            "pool_balance": round(pool, 0),
        })
    return {"weekly_data": weeks, "generated_at": datetime.now().isoformat()}

@router.get("/triggers")
async def trigger_analytics():
    """Payout trigger breakdown analytics"""
    return {
        "trigger_breakdown": {
            "workability_index": 42,
            "causation_model": 28,
            "both": 18,
        },
        "tier_distribution": {"T1": 35, "T2": 28, "T3": 22, "T4": 15},
        "avg_loss_pct": 43.2,
        "avg_payout_amount": 312,
        "total_payouts_this_month": 47,
    }
