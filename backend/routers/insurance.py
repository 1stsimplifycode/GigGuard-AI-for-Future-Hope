"""Insurance Router"""
from fastapi import APIRouter
from pydantic import BaseModel
from core.insurance_engine import insurance_engine

router = APIRouter()

class EnrollRequest(BaseModel):
    name: str
    phone: str
    platform: str
    city: str
    risk_level: str = "medium"

@router.post("/enroll")
async def enroll(req: EnrollRequest):
    partner = insurance_engine.enroll_partner(
        req.name, req.phone, req.platform, req.city, req.risk_level
    )
    return {"partner_id": partner.id, "weekly_premium": partner.weekly_premium, "status": "enrolled"}

@router.post("/premium/collect/{partner_id}")
async def collect_premium(partner_id: str):
    tx = insurance_engine.collect_premium(partner_id)
    if not tx:
        return {"error": "Partner not found or inactive"}
    return {"transaction_id": tx.id, "amount": tx.amount, "status": tx.status}

@router.get("/pool")
async def pool_summary():
    return insurance_engine.get_pool_summary()

@router.get("/payouts")
async def list_payouts():
    return [
        {
            "id": p.id, "partner_id": p.partner_id, "amount": p.amount,
            "tier": p.tier, "loss_percentage": p.loss_percentage,
            "processed_at": p.processed_at.isoformat(), "status": p.status,
        }
        for p in insurance_engine.payout_history[-50:]
    ]
