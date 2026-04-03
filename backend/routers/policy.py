"""Policy Router"""
from fastapi import APIRouter
from datetime import datetime, date
from models.risk_models import RiskTier, WEEKLY_PREMIUMS

router = APIRouter()

@router.get("/{partner_id}")
async def get_policy(partner_id: str):
    return {
        "partner_id": partner_id,
        "policy_number": f"GG-{partner_id}-2024",
        "status": "active",
        "risk_tier": "medium",
        "weekly_premium": 50,
        "coverage_start": "2024-01-15",
        "next_premium_due": str(date.today()),
        "total_premiums_paid": 650,
        "total_payouts_received": 180,
        "claims_count": 3,
    }

@router.get("/{partner_id}/history")
async def get_policy_history(partner_id: str):
    history = []
    for i in range(8):
        history.append({
            "week": f"Week {i+1}",
            "premium_paid": 50,
            "payout_received": [0, 0, 245, 0, 180, 0, 0, 320][i],
            "workability_avg": round(55 + (i * 3) % 30, 1),
        })
    return {"partner_id": partner_id, "history": history}
