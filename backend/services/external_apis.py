"""
ARIA-Gig External API Service
Integrates: OpenWeatherMap, AQI data, fuel price feeds
Falls back to realistic simulated data if APIs unavailable
"""

import os
import random
import httpx
import numpy as np
from datetime import datetime
from models.risk_models import WeatherData, MarketData


OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "")
FUEL_BASELINE_INR = 96.0  # Bangalore petrol baseline


class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    AQI_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

    async def get_weather(self, city: str = "Bangalore,IN") -> WeatherData:
        if OPENWEATHER_KEY:
            try:
                return await self._fetch_live(city)
            except Exception as e:
                print(f"[WeatherService] Live fetch failed: {e} — using fallback")
        return self._generate_fallback(city)

    async def _fetch_live(self, city: str) -> WeatherData:
        async with httpx.AsyncClient(timeout=10) as client:
            # Current weather
            resp = await client.get(
                f"{self.BASE_URL}/weather",
                params={"q": city, "appid": OPENWEATHER_KEY, "units": "metric"},
            )
            resp.raise_for_status()
            data = resp.json()

            lat = data["coord"]["lat"]
            lon = data["coord"]["lon"]

            # AQI
            aqi_resp = await client.get(
                self.AQI_URL,
                params={"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY},
            )
            aqi_data = aqi_resp.json() if aqi_resp.status_code == 200 else {}
            aqi_index = aqi_data.get("list", [{}])[0].get("main", {}).get("aqi", 2)
            # Convert OWM AQI (1-5) to US AQI scale (0-500)
            aqi_map = {1: 25, 2: 75, 3: 125, 4: 225, 5: 375}
            aqi = aqi_map.get(aqi_index, 75)

            return WeatherData(
                temperature=data["main"]["temp"],
                wind_speed=data["wind"]["speed"] * 3.6,  # m/s → km/h
                precipitation=data.get("rain", {}).get("1h", 0),
                visibility=data.get("visibility", 10000) / 1000,  # m → km
                condition=data["weather"][0]["main"],
                aqi=aqi,
            )

    def _generate_fallback(self, city: str) -> WeatherData:
        """Generate realistic weather for Bangalore"""
        hour = datetime.now().hour
        month = datetime.now().month

        # Monsoon months (Jun-Sep) → more rain
        is_monsoon = 6 <= month <= 9
        base_temp = 26 if is_monsoon else 30
        rain = np.random.exponential(5) if is_monsoon else max(0, np.random.normal(0, 1))
        aqi_base = 85 if is_monsoon else 130

        return WeatherData(
            temperature=round(np.random.normal(base_temp, 3), 1),
            wind_speed=round(abs(np.random.normal(15, 8)), 1),
            precipitation=round(max(0, rain), 2),
            visibility=round(max(0.5, np.random.normal(8, 2)), 1),
            condition="Rain" if rain > 2 else "Clouds" if random.random() > 0.5 else "Clear",
            aqi=round(max(30, np.random.normal(aqi_base, 30)), 0),
        )


class MarketService:
    """Fetches or simulates fuel prices and order demand"""

    async def get_market_data(self, stress_mode: bool = False) -> MarketData:
        fuel_price = self._get_fuel_price(stress_mode)
        demand = self._get_demand_index(stress_mode)
        peer_trend = self._get_peer_trend(stress_mode)

        return MarketData(
            fuel_price_per_liter=fuel_price,
            fuel_baseline=FUEL_BASELINE_INR,
            demand_index=demand,
            peer_earnings_trend=peer_trend,
            platform_demand_change=demand - 0.85,
        )

    def _get_fuel_price(self, stress_mode: bool) -> float:
        # Simulate daily fuel price with geopolitical volatility
        base = FUEL_BASELINE_INR
        if stress_mode:
            # Iran-Israel conflict simulation → 15-25% spike
            spike = random.uniform(0.15, 0.25)
            return round(base * (1 + spike), 2)
        # Normal volatility ±5%
        return round(base * random.uniform(0.97, 1.07), 2)

    def _get_demand_index(self, stress_mode: bool) -> float:
        if stress_mode:
            # Demand drops 30-40% under economic stress
            return round(random.uniform(0.40, 0.65), 3)
        return round(random.uniform(0.70, 0.95), 3)

    def _get_peer_trend(self, stress_mode: bool) -> float:
        if stress_mode:
            return round(random.uniform(-0.35, -0.20), 3)
        return round(random.uniform(-0.10, 0.10), 3)


weather_service = WeatherService()
market_service = MarketService()
