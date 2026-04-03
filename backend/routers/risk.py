"""
Risk Router — /api/v1/risk
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

from core.risk_engine import (
    ARIARiskEngine, WeatherInput, PollutionInput,
    EconomicInput, PeerTrendInput, IndividualInput
)
from services.api_integrations import (
    weather_client, aqi_client, economic_client, peer_client
)

router = APIRouter()
engine = ARIARiskEngine()


class AssessmentRequest(BaseModel):
    partner_id: str
    city: str = "bengaluru"
    actual_earnings: float
    expected_earnings: float
    hours_worked: float = 8.0
    expected_hours: float = 10.0
    voluntary_absence_hours: float = 0.0
    platform_ban: bool = False
    vehicle_failure: bool = False
    stress_mode: bool = False


@router.post("/assess")
async def assess_risk(req: AssessmentRequest):
    """Full risk assessment for a delivery partner"""
    weather_data = await weather_client.get_current(req.city)
    aqi_data = await aqi_client.get_aqi(req.city)
    economic_data = await economic_client.get_economic_data(req.city, req.stress_mode)
    peer_data = await peer_client.get_peer_data(req.city, req.stress_mode)

    weather = WeatherInput(**{
        k: weather_data[k] for k in ["temperature_c", "rainfall_mm", "wind_speed_kmh", "visibility_km", "storm_alert"]
    })
    pollution = PollutionInput(**{k: aqi_data[k] for k in ["aqi", "pm25", "hazardous_alert"]})
    economic = EconomicInput(**{
        k: economic_data[k] for k in ["fuel_price_per_liter", "baseline_fuel_price", "demand_index", "geopolitical_stress"]
    })
    peer = PeerTrendInput(**{
        k: peer_data[k] for k in ["active_riders_today", "baseline_active_riders", "avg_peer_earnings", "baseline_avg_peer_earnings"]
    })
    individual = IndividualInput(
        actual_earnings=req.actual_earnings,
        expected_earnings=req.expected_earnings,
        hours_worked=req.hours_worked,
        expected_hours=req.expected_hours,
        voluntary_absence_hours=req.voluntary_absence_hours,
        platform_ban=req.platform_ban,
        vehicle_failure=req.vehicle_failure,
    )

    result = engine.evaluate(weather, pollution, economic, peer, individual)

    payout_amount = None
    if result.payout_eligible and result.payout_rate:
        payout_amount = round(result.edi * result.payout_rate, 2)

    return {
        "partner_id": req.partner_id,
        "assessment": {
            "workability_score": result.workability_score,
            "edi": result.edi,
            "causation_score": result.causation_score,
            "loss_percentage": result.loss_percentage,
            "is_systemic": result.is_systemic,
            "payout_eligible": result.payout_eligible,
            "payout_tier": result.payout_tier,
            "payout_rate": result.payout_rate,
            "payout_amount": payout_amount,
            "exclusion_triggered": result.exclusion_triggered,
            "exclusion_reason": result.exclusion_reason,
            "risk_level": result.risk_level,
            "weekly_premium": result.weekly_premium,
        },
        "causation_breakdown": {
            "environment": result.environment_score,
            "peer_trend": result.peer_trend_score,
            "demand": result.demand_score,
            "individual_deviation": result.individual_deviation_score,
        },
        "environmental": {
            "weather": weather_data,
            "aqi": aqi_data,
            "economic": economic_data,
            "peer": peer_data,
        },
    }


@router.get("/workability")
async def get_workability(
    city: str = Query("bengaluru"),
    stress_mode: bool = Query(False),
):
    """Get current workability score for a city"""
    weather_data = await weather_client.get_current(city)
    aqi_data = await aqi_client.get_aqi(city)
    economic_data = await economic_client.get_economic_data(city, stress_mode)

    weather = WeatherInput(**{
        k: weather_data[k] for k in ["temperature_c", "rainfall_mm", "wind_speed_kmh", "visibility_km", "storm_alert"]
    })
    pollution = PollutionInput(**{k: aqi_data[k] for k in ["aqi", "pm25", "hazardous_alert"]})
    from core.config import settings
    economic = EconomicInput(
        fuel_price_per_liter=economic_data["fuel_price_per_liter"],
        baseline_fuel_price=economic_data["baseline_fuel_price"],
        demand_index=economic_data["demand_index"],
        geopolitical_stress=economic_data["geopolitical_stress"],
    )

    score = engine.compute_workability_score(weather, pollution, economic)
    return {
        "city": city,
        "workability_score": score,
        "stress_mode": stress_mode,
        "trigger_payout": score < settings.WORKABILITY_PAYOUT_THRESHOLD,
        "inputs": {
            "weather": weather_data,
            "aqi": aqi_data,
            "economic": economic_data,
        },
    }
