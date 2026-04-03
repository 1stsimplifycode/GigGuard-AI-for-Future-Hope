"""
Unit tests for ARIA-Gig Risk Engine
Tests: Workability Index, EDI, Causation Model, Payout Tiers, Exclusions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from services.risk_engine import RiskEngine
from models.risk_models import (
    WeatherData, MarketData, EarningsData, RiskTier, PayoutTier
)

engine = RiskEngine()

NORMAL_WEATHER = WeatherData(
    temperature=28.0, wind_speed=15.0, precipitation=0.0,
    visibility=10.0, condition="Clear", aqi=85.0
)
RAIN_WEATHER = WeatherData(
    temperature=26.0, wind_speed=35.0, precipitation=18.0,
    visibility=2.5, condition="Rain", aqi=95.0
)
STRESS_WEATHER = WeatherData(
    temperature=42.0, wind_speed=55.0, precipitation=25.0,
    visibility=1.2, condition="Thunderstorm", aqi=280.0
)
NORMAL_MARKET = MarketData(
    fuel_price_per_liter=98.0, fuel_baseline=96.0,
    demand_index=0.85, peer_earnings_trend=-0.05, platform_demand_change=-0.03
)
STRESS_MARKET = MarketData(
    fuel_price_per_liter=118.0, fuel_baseline=96.0,
    demand_index=0.45, peer_earnings_trend=-0.30, platform_demand_change=-0.32
)


class TestWorkabilityIndex:
    def test_normal_conditions_high_score(self):
        score = engine.compute_workability(NORMAL_WEATHER, NORMAL_MARKET)
        assert score.score >= 60, f"Expected ≥60, got {score.score}"
        assert not score.trigger_payout

    def test_rain_reduces_score(self):
        # RAIN_WEATHER has precipitation=18mm + wind=35kph → meaningful penalty vs clear sky
        score = engine.compute_workability(RAIN_WEATHER, NORMAL_MARKET)
        normal_score = engine.compute_workability(NORMAL_WEATHER, NORMAL_MARKET)
        assert score.score < normal_score.score, "Rain should reduce workability vs clear conditions"
        # Heavy rain (18mm) with strong wind (35kph) — penalty should be meaningful
        assert score.score < 90

    def test_stress_mode_triggers_payout(self):
        score = engine.compute_workability(STRESS_WEATHER, STRESS_MARKET, stress_mode=True)
        assert score.score < 50
        assert score.trigger_payout

    def test_score_within_bounds(self):
        for weather, market in [
            (NORMAL_WEATHER, NORMAL_MARKET),
            (RAIN_WEATHER, STRESS_MARKET),
            (STRESS_WEATHER, NORMAL_MARKET),
        ]:
            score = engine.compute_workability(weather, market)
            assert 0 <= score.score <= 100

    def test_high_aqi_penalty(self):
        high_aqi = WeatherData(**{**NORMAL_WEATHER.dict(), "aqi": 320.0})
        score = engine.compute_workability(high_aqi, NORMAL_MARKET)
        normal_score = engine.compute_workability(NORMAL_WEATHER, NORMAL_MARKET)
        assert score.score < normal_score.score


class TestEDI:
    def test_zero_loss(self):
        earnings = EarningsData(
            partner_id="P001", expected_daily=750, actual_daily=750,
            hours_worked=8, orders_completed=14
        )
        edi = engine.compute_edi(earnings)
        assert edi.edi_absolute == 0
        assert edi.edi_percentage == 0
        assert edi.loss_pct == 0

    def test_partial_loss(self):
        earnings = EarningsData(
            partner_id="P001", expected_daily=800, actual_daily=480,
            hours_worked=6, orders_completed=9
        )
        edi = engine.compute_edi(earnings)
        assert edi.edi_absolute == 320
        assert abs(edi.edi_percentage - 40.0) < 0.1
        assert abs(edi.loss_pct - 0.40) < 0.01

    def test_full_loss(self):
        earnings = EarningsData(
            partner_id="P001", expected_daily=750, actual_daily=0,
            hours_worked=0, orders_completed=0
        )
        edi = engine.compute_edi(earnings)
        assert edi.edi_percentage == 100.0

    def test_no_negative_deficit(self):
        # Actual > expected (good day) — EDI should be 0, not negative
        earnings = EarningsData(
            partner_id="P001", expected_daily=600, actual_daily=750,
            hours_worked=10, orders_completed=20
        )
        edi = engine.compute_edi(earnings)
        assert edi.edi_absolute == 0


class TestCausationModel:
    def test_systemic_under_stress(self):
        # Partner loss mirrors peer trend closely → low individual deviation → systemic
        earnings = EarningsData(
            partner_id="P001", expected_daily=750, actual_daily=525,
            hours_worked=5, orders_completed=8
        )  # ~30% loss, matching STRESS_MARKET peer_earnings_trend of -0.30
        causation = engine.compute_causation(STRESS_WEATHER, STRESS_MARKET, earnings, stress_mode=True)
        assert causation.is_systemic, (
            f"Expected systemic (>0.60) under extreme stress conditions, got {causation.causation_score}"
        )

    def test_individual_deviation_reduces_causation(self):
        # Normal conditions but partner earns far less than peers
        market_with_good_peers = MarketData(
            **{**NORMAL_MARKET.dict(), "peer_earnings_trend": 0.10}  # peers earning more
        )
        earnings_bad = EarningsData(
            partner_id="P001", expected_daily=750, actual_daily=200,
            hours_worked=2, orders_completed=3
        )
        causation = engine.compute_causation(NORMAL_WEATHER, market_with_good_peers, earnings_bad)
        # Individual deviation should penalize causation
        assert causation.individual_deviation > 0

    def test_causation_score_bounds(self):
        earnings = EarningsData(
            partner_id="P001", expected_daily=750, actual_daily=400,
            hours_worked=6, orders_completed=10
        )
        for weather, market in [(NORMAL_WEATHER, NORMAL_MARKET), (STRESS_WEATHER, STRESS_MARKET)]:
            c = engine.compute_causation(weather, market, earnings)
            assert 0 <= c.causation_score <= 1


class TestPayoutTiers:
    def _make_payout(self, loss_pct, score, cause, tier=RiskTier.MEDIUM):
        from models.risk_models import EDIResult, CausationResult, WorkabilityScore
        edi = EDIResult(
            partner_id="P001", expected_earnings=750,
            actual_earnings=750 * (1 - loss_pct),
            edi_absolute=750 * loss_pct,
            edi_percentage=loss_pct * 100,
            loss_pct=loss_pct,
        )
        workability = WorkabilityScore(
            score=score, weather_contribution=80, aqi_contribution=-5,
            fuel_contribution=-3, demand_contribution=-2,
            trigger_payout=score < 50, breakdown={}
        )
        causation = CausationResult(
            causation_score=cause, environment_factor=0.5, peer_trend_factor=0.4,
            demand_factor=0.4, individual_deviation=0.1,
            is_systemic=cause > 0.60, breakdown={}
        )
        earnings = EarningsData(
            partner_id="P001", expected_daily=750, actual_daily=750 * (1 - loss_pct),
            hours_worked=6, orders_completed=10
        )
        return engine.compute_payout(edi, causation, workability, earnings, tier)

    def test_t1_payout(self):
        result = self._make_payout(loss_pct=0.28, score=42, cause=0.75)
        assert result.eligible
        assert result.tier == PayoutTier.T1
        assert result.payout_rate == 0.50

    def test_t2_payout(self):
        result = self._make_payout(loss_pct=0.45, score=38, cause=0.80)
        assert result.eligible
        assert result.tier == PayoutTier.T2
        assert result.payout_rate == 0.65

    def test_t3_payout(self):
        result = self._make_payout(loss_pct=0.65, score=28, cause=0.85)
        assert result.eligible
        assert result.tier == PayoutTier.T3
        assert result.payout_rate == 0.75

    def test_t4_payout(self):
        result = self._make_payout(loss_pct=0.88, score=18, cause=0.90)
        assert result.eligible
        assert result.tier == PayoutTier.T4
        assert result.payout_rate == 0.85

    def test_no_payout_below_20pct(self):
        result = self._make_payout(loss_pct=0.15, score=42, cause=0.75)
        assert not result.eligible

    def test_no_payout_without_trigger(self):
        result = self._make_payout(loss_pct=0.35, score=72, cause=0.40)
        assert not result.eligible

    def test_exclusion_voluntary_absence(self):
        from models.risk_models import EDIResult, CausationResult, WorkabilityScore
        edi = EDIResult(partner_id="P001", expected_earnings=750, actual_earnings=200,
            edi_absolute=550, edi_percentage=73.3, loss_pct=0.733)
        workability = WorkabilityScore(score=35, weather_contribution=80,
            aqi_contribution=-5, fuel_contribution=-3, demand_contribution=-2,
            trigger_payout=True, breakdown={})
        causation = CausationResult(causation_score=0.75, environment_factor=0.7,
            peer_trend_factor=0.6, demand_factor=0.7, individual_deviation=0.1,
            is_systemic=True, breakdown={})
        earnings = EarningsData(partner_id="P001", expected_daily=750, actual_daily=200,
            hours_worked=0, orders_completed=0, voluntary_absence=True)
        result = engine.compute_payout(edi, causation, workability, earnings, RiskTier.MEDIUM)
        assert not result.eligible
        assert result.exclusion_applied is not None
        assert "voluntary" in result.exclusion_applied.lower()

    def test_high_tier_higher_premium(self):
        r_low = self._make_payout(0.45, 38, 0.80, RiskTier.LOW)
        r_high = self._make_payout(0.45, 38, 0.80, RiskTier.HIGH)
        assert r_high.weekly_premium > r_low.weekly_premium


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
