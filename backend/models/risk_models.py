"""
ARIA-Gig Risk Engine Models
Earnings Deficit Index, Causation Model, Workability Index, Payout Tiers
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PayoutTier(str, Enum):
    T1 = "T1"  # 20-35% loss → 50% payout
    T2 = "T2"  # 35-55% loss → 65% payout
    T3 = "T3"  # 55-75% loss → 75% payout
    T4 = "T4"  # 75-100% loss → 85% payout
    NONE = "NONE"  # No payout


PAYOUT_TIERS = {
    PayoutTier.T1: {"loss_min": 0.20, "loss_max": 0.35, "payout_rate": 0.50},
    PayoutTier.T2: {"loss_min": 0.35, "loss_max": 0.55, "payout_rate": 0.65},
    PayoutTier.T3: {"loss_min": 0.55, "loss_max": 0.75, "payout_rate": 0.75},
    PayoutTier.T4: {"loss_min": 0.75, "loss_max": 1.00, "payout_rate": 0.85},
}

WEEKLY_PREMIUMS = {
    RiskTier.LOW: 30,
    RiskTier.MEDIUM: 50,
    RiskTier.HIGH: 70,
}


class WeatherData(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    wind_speed: float = Field(..., description="Wind speed in km/h")
    precipitation: float = Field(..., description="Rainfall in mm")
    visibility: float = Field(..., description="Visibility in km")
    condition: str = Field(..., description="Weather condition code")
    aqi: float = Field(..., description="Air Quality Index (0-500)")


class MarketData(BaseModel):
    fuel_price_per_liter: float = Field(..., description="Fuel price in INR/liter")
    fuel_baseline: float = Field(default=96.0, description="Baseline fuel price INR/liter")
    demand_index: float = Field(..., description="Relative order demand (0-1)")
    peer_earnings_trend: float = Field(..., description="Peer earnings change ratio (-1 to 1)")
    platform_demand_change: float = Field(..., description="Platform demand change ratio")


class EarningsData(BaseModel):
    partner_id: str
    expected_daily: float = Field(..., description="Expected daily earnings in INR")
    actual_daily: float = Field(..., description="Actual daily earnings in INR")
    hours_worked: float = Field(..., description="Hours worked today")
    orders_completed: int = Field(..., description="Orders completed today")
    voluntary_absence: bool = Field(default=False)
    platform_banned: bool = Field(default=False)
    vehicle_failure: bool = Field(default=False)


class WorkabilityScore(BaseModel):
    score: float = Field(..., ge=0, le=100, description="Workability score 0-100")
    weather_contribution: float
    aqi_contribution: float
    fuel_contribution: float
    demand_contribution: float
    trigger_payout: bool = Field(..., description="True if score < 50")
    breakdown: dict


class EDIResult(BaseModel):
    partner_id: str
    expected_earnings: float
    actual_earnings: float
    edi_absolute: float = Field(..., description="EDI in INR")
    edi_percentage: float = Field(..., description="EDI as % of expected")
    loss_pct: float


class CausationResult(BaseModel):
    causation_score: float = Field(..., ge=0, le=1)
    environment_factor: float
    peer_trend_factor: float
    demand_factor: float
    individual_deviation: float
    is_systemic: bool = Field(..., description="True if causation > 0.6")
    breakdown: dict


class PayoutResult(BaseModel):
    partner_id: str
    eligible: bool
    tier: PayoutTier
    loss_percentage: float
    payout_rate: float
    payout_amount: float
    weekly_premium: float
    net_payout: float
    reason: str
    exclusion_applied: Optional[str] = None


class RiskAssessmentRequest(BaseModel):
    partner_id: str
    weather: WeatherData
    market: MarketData
    earnings: EarningsData
    risk_tier: RiskTier = RiskTier.MEDIUM
    economic_stress_mode: bool = False


class RiskAssessmentResponse(BaseModel):
    partner_id: str
    workability: WorkabilityScore
    edi: EDIResult
    causation: CausationResult
    payout: PayoutResult
    risk_tier: RiskTier
    timestamp: str
    stress_mode_active: bool
