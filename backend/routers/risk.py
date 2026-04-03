"""
Risk Engine API Router
POST /api/v1/risk/assess — Full risk assessment
GET  /api/v1/risk/workability — Live workability score
GET  /api/v1/risk/stress-test — Economic stress simulation
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from models.risk_models import (
    RiskAssessmentRequest, RiskAssessmentResponse,
    WeatherData, MarketData, EarningsData, RiskTier
)
from services.risk_engine import risk_engine
from services.external_apis import weather_service, market_service

router = APIRouter()


@router.post("/assess", response_model=RiskAssessmentResponse)
async def assess_risk(request: RiskAssessmentRequest):
    """
    Full risk assessment for a delivery partner.
    Computes: Workability Index, EDI, Causation Score, Payout Eligibility.
    """
    try:
        workability = risk_engine.compute_workability(
            request.weather, request.market, request.economic_stress_mode
        )
        edi = risk_engine.compute_edi(request.earnings)
        causation = risk_engine.compute_causation(
            request.weather, request.market, request.earnings, request.economic_stress_mode
        )
        payout = risk_engine.compute_payout(
            edi, causation, workability, request.earnings, request.risk_tier
        )

        return RiskAssessmentResponse(
            partner_id=request.partner_id,
            workability=workability,
            edi=edi,
            causation=causation,
            payout=payout,
            risk_tier=request.risk_tier,
            timestamp=datetime.now().isoformat(),
            stress_mode_active=request.economic_stress_mode,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workability")
async def get_workability(city: str = "Bangalore,IN", stress_mode: bool = False):
    """Live workability score using real-time weather and market data"""
    weather = await weather_service.get_weather(city)
    market = await market_service.get_market_data(stress_mode)
    score = risk_engine.compute_workability(weather, market, stress_mode)
    return {
        "city": city,
        "workability": score,
        "weather": weather,
        "market": market,
        "stress_mode": stress_mode,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/stress-test")
async def stress_test(partner_id: str = "P001"):
    """
    Simulate Economic Stress Mode (geopolitical disruption scenario).
    Models: fuel price spike (+20%), demand collapse (-35%), AQI increase (+30%).
    """
    weather = await weather_service.get_weather()
    market = await market_service.get_market_data(stress_mode=True)

    earnings = EarningsData(
        partner_id=partner_id,
        expected_daily=800,
        actual_daily=320,
        hours_worked=6,
        orders_completed=8,
    )

    workability = risk_engine.compute_workability(weather, market, stress_mode=True)
    edi = risk_engine.compute_edi(earnings)
    causation = risk_engine.compute_causation(weather, market, earnings, stress_mode=True)
    payout = risk_engine.compute_payout(edi, causation, workability, earnings, RiskTier.MEDIUM)

    return {
        "scenario": "Economic Stress Mode — Geopolitical Disruption",
        "description": "Simulates Iran-Israel conflict impact: fuel +20%, demand -35%, AQI +30%",
        "partner_id": partner_id,
        "workability": workability,
        "edi": edi,
        "causation": causation,
        "payout": payout,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/payout-tiers")
async def get_payout_tiers():
    """Return payout tier configuration"""
    return {
        "tiers": [
            {"tier": "T1", "loss_range": "20-35%", "payout_rate": "50%", "description": "Mild disruption"},
            {"tier": "T2", "loss_range": "35-55%", "payout_rate": "65%", "description": "Moderate disruption"},
            {"tier": "T3", "loss_range": "55-75%", "payout_rate": "75%", "description": "Severe disruption"},
            {"tier": "T4", "loss_range": "75-100%", "payout_rate": "85%", "description": "Extreme disruption"},
        ],
        "premiums": {
            "low": {"weekly": 30, "monthly": 120},
            "medium": {"weekly": 50, "monthly": 200},
            "high": {"weekly": 70, "monthly": 280},
        },
        "coverage": {
            "covered": [
                "Income loss from weather disruptions",
                "Income loss from high AQI/pollution",
                "Income loss from demand fluctuations",
                "Income loss from fuel price spikes (indirect)",
                "Income loss from geopolitical supply chain effects",
            ],
            "excluded": [
                "Voluntary absence from platform",
                "Platform ban or deactivation",
                "Vehicle mechanical failure",
                "Direct war damage or injury",
                "Direct pandemic impact (not economic effects)",
            ],
        },
    }
