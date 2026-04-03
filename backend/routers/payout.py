"""Payout Router"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/{partner_id}/history")
async def payout_history(partner_id: str):
    payouts = [
        {"date": "2024-12-02", "amount": 245, "tier": "T2", "reason": "Heavy rainfall — Workability 38"},
        {"date": "2024-11-18", "amount": 180, "tier": "T1", "reason": "High AQI 215 — Causation 0.72"},
        {"date": "2024-10-25", "amount": 320, "tier": "T3", "reason": "Cyclone warning — Workability 22"},
    ]
    return {"partner_id": partner_id, "payouts": payouts, "total": sum(p["amount"] for p in payouts)}
