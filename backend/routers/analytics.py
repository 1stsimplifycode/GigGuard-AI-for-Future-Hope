"""Analytics Router"""
from fastapi import APIRouter
import random

router = APIRouter()

@router.get("/earnings-trend/{partner_id}")
async def earnings_trend(partner_id: str, days: int = 30):
    trend = []
    base = 850
    for i in range(days):
        actual = base * random.uniform(0.55, 1.05)
        expected = base * random.uniform(0.90, 1.05)
        trend.append({
            "day": i + 1,
            "actual_earnings": round(actual, 2),
            "expected_earnings": round(expected, 2),
            "edi": round(max(0, expected - actual), 2),
        })
    return {"partner_id": partner_id, "trend": trend}

@router.get("/city-heatmap")
async def city_heatmap():
    cities = ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune"]
    return [
        {
            "city": c,
            "workability_score": random.randint(30, 85),
            "active_partners": random.randint(800, 5000),
            "avg_edi": random.randint(80, 350),
            "payouts_today": random.randint(0, 120),
        }
        for c in cities
    ]
