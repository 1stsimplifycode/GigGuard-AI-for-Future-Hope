"""
ARIA-Gig Core Risk Engine
Implements: Workability Index, EDI, Causation Model, Payout Tiers
"""

import numpy as np
from datetime import datetime
from models.risk_models import (
    WeatherData, MarketData, EarningsData, RiskTier,
    WorkabilityScore, EDIResult, CausationResult, PayoutResult,
    PayoutTier, PAYOUT_TIERS, WEEKLY_PREMIUMS, RiskAssessmentResponse
)


class RiskEngine:
    """
    Core ARIA-Gig risk computation engine.

    Models:
    -------
    1. Workability Index  → Score 0-100 based on env + fuel + demand
    2. EDI               → Expected − Actual earnings
    3. Causation Model   → Determines if loss is systemic (not voluntary)
    4. Payout Calculator → Tier-based compensation
    """

    # Workability thresholds
    WORKABILITY_TRIGGER = 50.0

    # Weather penalty coefficients
    WEATHER_WEIGHTS = {
        "temperature_extreme": 0.15,   # >40°C or <5°C
        "wind_speed": 0.20,            # >40 km/h
        "precipitation": 0.25,         # >5mm
        "visibility": 0.15,            # <2km
        "aqi": 0.25,                   # >150 AQI
    }

    # Causation model weights
    CAUSATION_WEIGHTS = {
        "environment": 0.40,
        "peer_trends": 0.30,
        "demand": 0.30,
        "individual_deviation_penalty": -0.25,
    }

    def compute_workability(
        self,
        weather: WeatherData,
        market: MarketData,
        stress_mode: bool = False
    ) -> WorkabilityScore:
        """
        Workability Index: composite score 0-100
        Score < 50 → triggers payout eligibility
        """
        score = 100.0
        breakdown = {}

        # --- Weather component (max penalty: 40 pts) ---
        weather_penalty = 0.0

        # Temperature extreme (>40°C or <5°C)
        if weather.temperature > 40 or weather.temperature < 5:
            temp_pen = min(15, abs(weather.temperature - 25) * 0.5)
            weather_penalty += temp_pen
            breakdown["temperature"] = round(-temp_pen, 2)
        else:
            breakdown["temperature"] = 0

        # Wind speed
        if weather.wind_speed > 40:
            wind_pen = min(12, (weather.wind_speed - 40) * 0.3)
            weather_penalty += wind_pen
            breakdown["wind"] = round(-wind_pen, 2)
        elif weather.wind_speed > 25:
            wind_pen = (weather.wind_speed - 25) * 0.15
            weather_penalty += wind_pen
            breakdown["wind"] = round(-wind_pen, 2)
        else:
            breakdown["wind"] = 0

        # Precipitation
        if weather.precipitation > 10:
            rain_pen = min(15, weather.precipitation * 0.8)
            weather_penalty += rain_pen
            breakdown["precipitation"] = round(-rain_pen, 2)
        elif weather.precipitation > 3:
            rain_pen = weather.precipitation * 0.4
            weather_penalty += rain_pen
            breakdown["precipitation"] = round(-rain_pen, 2)
        else:
            breakdown["precipitation"] = 0

        # AQI penalty (max 20 pts)
        aqi_penalty = 0.0
        aqi = weather.aqi
        if stress_mode:
            aqi = min(500, aqi * 1.3)  # 30% worse in stress mode
        if aqi > 300:
            aqi_penalty = 20.0
        elif aqi > 200:
            aqi_penalty = 15.0
        elif aqi > 150:
            aqi_penalty = 10.0
        elif aqi > 100:
            aqi_penalty = 5.0
        breakdown["aqi"] = round(-aqi_penalty, 2)

        # Fuel price penalty (max 20 pts)
        fuel_price = market.fuel_price_per_liter
        if stress_mode:
            fuel_price *= 1.20  # 20% spike in stress mode
        fuel_ratio = fuel_price / market.fuel_baseline
        fuel_penalty = 0.0
        if fuel_ratio > 1.30:
            fuel_penalty = 20.0
        elif fuel_ratio > 1.20:
            fuel_penalty = 14.0
        elif fuel_ratio > 1.10:
            fuel_penalty = 8.0
        elif fuel_ratio > 1.05:
            fuel_penalty = 4.0
        breakdown["fuel_price"] = round(-fuel_penalty, 2)

        # Demand index penalty (max 20 pts)
        demand = market.demand_index
        if stress_mode:
            demand = max(0, demand * 0.65)  # 35% drop in stress mode
        demand_penalty = 0.0
        if demand < 0.3:
            demand_penalty = 20.0
        elif demand < 0.5:
            demand_penalty = 15.0
        elif demand < 0.7:
            demand_penalty = 8.0
        elif demand < 0.85:
            demand_penalty = 3.0
        breakdown["demand"] = round(-demand_penalty, 2)

        total_penalty = weather_penalty + aqi_penalty + fuel_penalty + demand_penalty
        score = max(0, 100 - total_penalty)

        # Stress mode floor
        if stress_mode:
            score = min(score, 42.0)

        return WorkabilityScore(
            score=round(score, 1),
            weather_contribution=round(100 - weather_penalty, 1),
            aqi_contribution=round(-aqi_penalty, 1),
            fuel_contribution=round(-fuel_penalty, 1),
            demand_contribution=round(-demand_penalty, 1),
            trigger_payout=score < self.WORKABILITY_TRIGGER,
            breakdown=breakdown,
        )

    def compute_edi(self, earnings: EarningsData) -> EDIResult:
        """
        Earnings Deficit Index
        EDI = Expected Earnings - Actual Earnings
        """
        edi_absolute = earnings.expected_daily - earnings.actual_daily
        edi_pct = (edi_absolute / earnings.expected_daily * 100) if earnings.expected_daily > 0 else 0
        loss_pct = max(0, edi_pct) / 100

        return EDIResult(
            partner_id=earnings.partner_id,
            expected_earnings=round(earnings.expected_daily, 2),
            actual_earnings=round(earnings.actual_daily, 2),
            edi_absolute=round(max(0, edi_absolute), 2),
            edi_percentage=round(max(0, edi_pct), 2),
            loss_pct=round(loss_pct, 4),
        )

    def compute_causation(
        self,
        weather: WeatherData,
        market: MarketData,
        earnings: EarningsData,
        stress_mode: bool = False
    ) -> CausationResult:
        """
        Causation Model:
        Causation = 0.40 × Environment + 0.30 × Peer_Trends + 0.30 × Demand − 0.25 × Individual_Deviation

        Score > 0.6 → systemic (eligible for payout)
        Score <= 0.6 → individual/voluntary (not eligible)
        """
        # Environment factor (weather + AQI combined)
        env_score = self._compute_env_factor(weather, stress_mode)

        # Peer trends factor (how much peer earnings dropped)
        peer_factor = self._compute_peer_factor(market)

        # Demand factor (platform-level demand collapse)
        demand_factor = self._compute_demand_factor(market, stress_mode)

        # Individual deviation (penalizes if partner's loss is far above peers)
        # High individual deviation → less systemic, more personal
        individual_deviation = self._compute_individual_deviation(earnings, market)

        causation = (
            self.CAUSATION_WEIGHTS["environment"] * env_score
            + self.CAUSATION_WEIGHTS["peer_trends"] * peer_factor
            + self.CAUSATION_WEIGHTS["demand"] * demand_factor
            + self.CAUSATION_WEIGHTS["individual_deviation_penalty"] * individual_deviation
        )

        causation = float(np.clip(causation, 0, 1))

        return CausationResult(
            causation_score=round(causation, 4),
            environment_factor=round(env_score, 4),
            peer_trend_factor=round(peer_factor, 4),
            demand_factor=round(demand_factor, 4),
            individual_deviation=round(individual_deviation, 4),
            is_systemic=causation > 0.60,
            breakdown={
                "env_weighted": round(0.40 * env_score, 4),
                "peer_weighted": round(0.30 * peer_factor, 4),
                "demand_weighted": round(0.30 * demand_factor, 4),
                "individual_penalty": round(-0.25 * individual_deviation, 4),
            },
        )

    def compute_payout(
        self,
        edi: EDIResult,
        causation: CausationResult,
        workability: WorkabilityScore,
        earnings: EarningsData,
        risk_tier: RiskTier,
    ) -> PayoutResult:
        """
        Determine payout tier and amount.

        Eligibility:
        1. Workability score < 50 OR causation > 0.6
        2. Loss >= 20%
        3. No exclusion applies
        """
        weekly_premium = WEEKLY_PREMIUMS[risk_tier]
        daily_premium = weekly_premium / 7

        # Check exclusions first
        exclusion = self._check_exclusions(earnings)
        if exclusion:
            return PayoutResult(
                partner_id=earnings.partner_id,
                eligible=False,
                tier=PayoutTier.NONE,
                loss_percentage=edi.loss_pct,
                payout_rate=0,
                payout_amount=0,
                weekly_premium=weekly_premium,
                net_payout=0,
                reason="Excluded from coverage",
                exclusion_applied=exclusion,
            )

        # Check eligibility triggers
        workability_trigger = workability.trigger_payout
        causation_trigger = causation.is_systemic
        loss_pct = edi.loss_pct

        if not (workability_trigger or causation_trigger):
            return PayoutResult(
                partner_id=earnings.partner_id,
                eligible=False,
                tier=PayoutTier.NONE,
                loss_percentage=loss_pct,
                payout_rate=0,
                payout_amount=0,
                weekly_premium=weekly_premium,
                net_payout=0,
                reason="No systemic trigger detected (workability OK, causation score below threshold)",
            )

        if loss_pct < 0.20:
            return PayoutResult(
                partner_id=earnings.partner_id,
                eligible=False,
                tier=PayoutTier.NONE,
                loss_percentage=loss_pct,
                payout_rate=0,
                payout_amount=0,
                weekly_premium=weekly_premium,
                net_payout=0,
                reason="Loss below minimum threshold (20%)",
            )

        # Determine payout tier
        tier = PayoutTier.NONE
        payout_rate = 0.0
        for t, config in PAYOUT_TIERS.items():
            if config["loss_min"] <= loss_pct <= config["loss_max"]:
                tier = t
                payout_rate = config["payout_rate"]
                break
        if loss_pct > 0.75:
            tier = PayoutTier.T4
            payout_rate = 0.85

        payout_amount = edi.edi_absolute * payout_rate
        net_payout = max(0, payout_amount - daily_premium)

        reason = (
            f"Systemic loss detected via {'Workability Index' if workability_trigger else 'Causation Model'}. "
            f"Loss: {round(loss_pct * 100, 1)}% | Tier: {tier.value}"
        )

        return PayoutResult(
            partner_id=earnings.partner_id,
            eligible=True,
            tier=tier,
            loss_percentage=round(loss_pct, 4),
            payout_rate=payout_rate,
            payout_amount=round(payout_amount, 2),
            weekly_premium=weekly_premium,
            net_payout=round(net_payout, 2),
            reason=reason,
        )

    # --- Private helpers ---

    def _compute_env_factor(self, weather: WeatherData, stress_mode: bool) -> float:
        penalty = 0.0
        if weather.temperature > 40 or weather.temperature < 5:
            penalty += 0.2
        if weather.wind_speed > 40:
            penalty += 0.2
        elif weather.wind_speed > 25:
            penalty += 0.1
        if weather.precipitation > 10:
            penalty += 0.25
        elif weather.precipitation > 3:
            penalty += 0.12
        aqi = weather.aqi * (1.3 if stress_mode else 1.0)
        if aqi > 300:
            penalty += 0.35
        elif aqi > 200:
            penalty += 0.25
        elif aqi > 150:
            penalty += 0.15
        return float(np.clip(penalty, 0, 1))

    def _compute_peer_factor(self, market: MarketData) -> float:
        peer_drop = -market.peer_earnings_trend
        return float(np.clip(peer_drop, 0, 1))

    def _compute_demand_factor(self, market: MarketData, stress_mode: bool) -> float:
        demand = market.demand_index * (0.65 if stress_mode else 1.0)
        return float(np.clip(1 - demand, 0, 1))

    def _compute_individual_deviation(self, earnings: EarningsData, market: MarketData) -> float:
        if earnings.expected_daily == 0:
            return 0
        personal_loss = max(0, (earnings.expected_daily - earnings.actual_daily) / earnings.expected_daily)
        peer_loss = max(0, -market.peer_earnings_trend)
        deviation = abs(personal_loss - peer_loss)
        # High deviation → more individual, penalize causation
        return float(np.clip(deviation * 2, 0, 1))

    def _check_exclusions(self, earnings: EarningsData) -> str | None:
        if earnings.voluntary_absence:
            return "Voluntary absence from platform"
        if earnings.platform_banned:
            return "Platform ban/deactivation"
        if earnings.vehicle_failure:
            return "Vehicle mechanical failure"
        return None


# Singleton engine
risk_engine = RiskEngine()
