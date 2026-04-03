"""
ARIA-Gig Risk Engine
Implements: EDI, Causation Model, Workability Index, Payout Tiers
"""
import numpy as np
from dataclasses import dataclass
from typing import Optional
from core.config import settings


@dataclass
class WeatherInput:
    temperature_c: float
    rainfall_mm: float
    wind_speed_kmh: float
    visibility_km: float
    storm_alert: bool = False


@dataclass
class PollutionInput:
    aqi: int                    # Air Quality Index
    pm25: float                 # PM2.5 µg/m³
    hazardous_alert: bool = False


@dataclass
class EconomicInput:
    fuel_price_per_liter: float
    baseline_fuel_price: float  # historical 30-day average
    demand_index: float         # 0–1 (1 = normal demand)
    geopolitical_stress: float  # 0–1 (0 = stable, 1 = crisis)


@dataclass
class PeerTrendInput:
    active_riders_today: int
    baseline_active_riders: int
    avg_peer_earnings: float
    baseline_avg_peer_earnings: float


@dataclass
class IndividualInput:
    actual_earnings: float
    expected_earnings: float
    hours_worked: float
    expected_hours: float
    voluntary_absence_hours: float = 0.0
    platform_ban: bool = False
    vehicle_failure: bool = False


@dataclass
class RiskEngineOutput:
    workability_score: float            # 0–100
    edi: float                          # Earnings Deficit Index
    causation_score: float              # 0–1
    environment_score: float
    peer_trend_score: float
    demand_score: float
    individual_deviation_score: float
    is_systemic: bool
    payout_eligible: bool
    payout_tier: Optional[int]
    payout_rate: Optional[float]
    loss_percentage: float
    exclusion_triggered: bool
    exclusion_reason: Optional[str]
    risk_level: str                     # low / medium / high
    weekly_premium: int


class ARIARiskEngine:
    """
    ARIA (Adaptive Risk Intelligence Architecture) — Core Risk Engine
    """

    def compute_workability_score(
        self,
        weather: WeatherInput,
        pollution: PollutionInput,
        economic: EconomicInput,
    ) -> float:
        """
        Workability Index: 0–100 composite score
        Higher = better working conditions
        """
        # Weather component (0–100)
        weather_score = 100.0
        if weather.storm_alert:
            weather_score -= 40
        weather_score -= min(weather.rainfall_mm * 2, 30)
        weather_score -= max(0, (weather.wind_speed_kmh - 30) * 0.5)
        if weather.visibility_km < 1:
            weather_score -= 20
        elif weather.visibility_km < 3:
            weather_score -= 10
        weather_score = max(0, min(100, weather_score))

        # AQI component (0–100)
        aqi_score = 100.0
        if pollution.aqi > 300:
            aqi_score = 10
        elif pollution.aqi > 200:
            aqi_score = 30
        elif pollution.aqi > 150:
            aqi_score = 50
        elif pollution.aqi > 100:
            aqi_score = 70
        elif pollution.aqi > 50:
            aqi_score = 90
        if pollution.hazardous_alert:
            aqi_score = min(aqi_score, 20)

        # Fuel price component (0–100)
        fuel_change_pct = (economic.fuel_price_per_liter - economic.baseline_fuel_price) / economic.baseline_fuel_price
        fuel_score = max(0, 100 - (fuel_change_pct * 200))  # -10% fuel spike = -20 pts

        # Demand component (0–100)
        demand_score = economic.demand_index * 100

        # Geopolitical stress modifier
        geo_modifier = (1 - economic.geopolitical_stress * 0.3)

        # Weighted workability
        workability = (
            0.30 * weather_score +
            0.25 * aqi_score +
            0.20 * fuel_score +
            0.25 * demand_score
        ) * geo_modifier

        return round(max(0, min(100, workability)), 2)

    def compute_edi(self, individual: IndividualInput) -> float:
        """
        Earnings Deficit Index: Expected − Actual Earnings (₹)
        """
        adjusted_expected = individual.expected_earnings * (
            individual.hours_worked / max(individual.expected_hours, 1)
        ) if individual.hours_worked < individual.expected_hours else individual.expected_earnings

        return max(0.0, adjusted_expected - individual.actual_earnings)

    def compute_causation_score(
        self,
        weather: WeatherInput,
        pollution: PollutionInput,
        economic: EconomicInput,
        peer: PeerTrendInput,
        individual: IndividualInput,
    ) -> dict:
        """
        Causation = 0.40 × Environment + 0.30 × Peer Trends + 0.30 × Demand − 0.25 × Individual Deviation
        Returns component scores + final causation
        """
        # Environment factor (0–1): bad weather + high AQI = high environment impact
        env_weather = min(1.0, (weather.rainfall_mm / 50 + (1 if weather.storm_alert else 0)) / 2)
        env_aqi = min(1.0, max(0, pollution.aqi - 100) / 200)
        environment = (env_weather * 0.5 + env_aqi * 0.5)

        # Peer trend factor (0–1): if peers also earning less, systemic
        peer_drop = 1 - (peer.avg_peer_earnings / max(peer.baseline_avg_peer_earnings, 1))
        peer_trend = max(0, min(1, peer_drop))

        # Demand factor (0–1): demand drop = systemic
        demand = max(0, 1 - economic.demand_index)

        # Individual deviation (0–1): voluntary absence = not systemic
        if individual.expected_hours > 0:
            voluntary_ratio = individual.voluntary_absence_hours / individual.expected_hours
        else:
            voluntary_ratio = 0
        individual_deviation = min(1.0, voluntary_ratio)

        causation = (
            0.40 * environment +
            0.30 * peer_trend +
            0.30 * demand -
            0.25 * individual_deviation
        )
        causation = max(0, min(1, causation))

        return {
            "environment": round(environment, 4),
            "peer_trend": round(peer_trend, 4),
            "demand": round(demand, 4),
            "individual_deviation": round(individual_deviation, 4),
            "causation_score": round(causation, 4),
        }

    def determine_payout_tier(self, loss_pct: float) -> tuple[Optional[int], Optional[float]]:
        """Returns (tier, payout_rate) based on loss percentage"""
        s = settings
        if loss_pct >= s.PAYOUT_TIER_4_MIN:
            return 4, s.PAYOUT_TIER_4_RATE
        elif loss_pct >= s.PAYOUT_TIER_3_MIN:
            return 3, s.PAYOUT_TIER_3_RATE
        elif loss_pct >= s.PAYOUT_TIER_2_MIN:
            return 2, s.PAYOUT_TIER_2_RATE
        elif loss_pct >= s.PAYOUT_TIER_1_MIN:
            return 1, s.PAYOUT_TIER_1_RATE
        return None, None

    def compute_risk_level(self, workability: float, causation: float) -> tuple[str, int]:
        """Determines risk tier and weekly premium"""
        if workability < 35 or causation > 0.7:
            return "high", settings.PREMIUM_HIGH_RISK
        elif workability < 60 or causation > 0.4:
            return "medium", settings.PREMIUM_MEDIUM_RISK
        return "low", settings.PREMIUM_LOW_RISK

    def check_exclusions(self, individual: IndividualInput) -> tuple[bool, Optional[str]]:
        """Check for policy exclusions"""
        if individual.platform_ban:
            return True, "Platform ban — not covered under policy"
        if individual.vehicle_failure:
            return True, "Vehicle failure — mechanical exclusion applies"
        if individual.voluntary_absence_hours >= individual.expected_hours * 0.8:
            return True, "Voluntary absence exceeds 80% of expected hours"
        return False, None

    def evaluate(
        self,
        weather: WeatherInput,
        pollution: PollutionInput,
        economic: EconomicInput,
        peer: PeerTrendInput,
        individual: IndividualInput,
    ) -> RiskEngineOutput:
        """
        Full risk evaluation pipeline
        """
        # Exclusion check first
        exclusion, exclusion_reason = self.check_exclusions(individual)

        # Core computations
        workability = self.compute_workability_score(weather, pollution, economic)
        edi = self.compute_edi(individual)
        causation_data = self.compute_causation_score(weather, pollution, economic, peer, individual)
        causation = causation_data["causation_score"]

        # Loss percentage
        if individual.expected_earnings > 0:
            loss_pct = min(1.0, edi / individual.expected_earnings)
        else:
            loss_pct = 0.0

        # Systemic determination: causation > 0.4 AND workability < 50
        is_systemic = causation >= 0.4 and workability < settings.WORKABILITY_PAYOUT_THRESHOLD

        # Payout eligibility
        tier, payout_rate = self.determine_payout_tier(loss_pct)
        payout_eligible = (
            not exclusion and
            is_systemic and
            tier is not None and
            workability < settings.WORKABILITY_PAYOUT_THRESHOLD
        )

        risk_level, premium = self.compute_risk_level(workability, causation)

        return RiskEngineOutput(
            workability_score=workability,
            edi=round(edi, 2),
            causation_score=causation,
            environment_score=causation_data["environment"],
            peer_trend_score=causation_data["peer_trend"],
            demand_score=causation_data["demand"],
            individual_deviation_score=causation_data["individual_deviation"],
            is_systemic=is_systemic,
            payout_eligible=payout_eligible,
            payout_tier=tier,
            payout_rate=payout_rate,
            loss_percentage=round(loss_pct * 100, 2),
            exclusion_triggered=exclusion,
            exclusion_reason=exclusion_reason,
            risk_level=risk_level,
            weekly_premium=premium,
        )
