"""Partners Router"""
from fastapi import APIRouter
import random

router = APIRouter()

@router.get("/{partner_id}/summary")
async def partner_summary(partner_id: str):
    return {
        "partner_id": partner_id,
        "name": "Ravi Kumar",
        "city": "Bengaluru",
        "platform": "Swiggy",
        "risk_level": "medium",
        "weekly_premium": 50,
        "policy_active": True,
        "total_premiums_paid": 1450,
        "total_payouts_received": 620,
        "active_since": "2024-01-15",
        "payout_history": [
            {"date": "2024-03-01", "amount": 320, "tier": 2, "reason": "Heavy rain + AQI spike"},
            {"date": "2024-02-10", "amount": 300, "tier": 1, "reason": "Demand drop — festival"},
        ],
    }
