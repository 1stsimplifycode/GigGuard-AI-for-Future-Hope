"""
External API Integrations — ARIA-Gig
OpenWeather, Economic Data, HazardHub (with simulation fallback)
"""
import httpx
import random
import math
from datetime import datetime
from core.config import settings


CITY_COORDS = {
    "bengaluru": (12.9716, 77.5946),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "pune": (18.5204, 73.8567),
}


class OpenWeatherClient:
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    async def get_current(self, city: str) -> dict:
        if not settings.OPENWEATHER_API_KEY:
            return self._simulate(city)

        lat, lon = CITY_COORDS.get(city.lower(), (12.9716, 77.5946))
        params = {
            "lat": lat, "lon": lon,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric",
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                r = await client.get(f"{self.BASE_URL}/weather", params=params)
                r.raise_for_status()
                d = r.json()
                return {
                    "temperature_c": d["main"]["temp"],
                    "rainfall_mm": d.get("rain", {}).get("1h", 0),
                    "wind_speed_kmh": d["wind"]["speed"] * 3.6,
                    "visibility_km": d.get("visibility", 10000) / 1000,
                    "storm_alert": d["weather"][0]["main"] in ("Thunderstorm", "Tornado"),
                    "description": d["weather"][0]["description"],
                    "source": "live",
                }
            except Exception:
                return self._simulate(city)

    def _simulate(self, city: str) -> dict:
        """Realistic simulation based on season and city"""
        now = datetime.utcnow()
        month = now.month
        hour = now.hour

        # Monsoon simulation (June–September for South India)
        is_monsoon = month in range(6, 10) and city.lower() in ("bengaluru", "chennai", "mumbai")
        rain = random.uniform(5, 40) if is_monsoon else random.uniform(0, 5)
        storm = is_monsoon and random.random() < 0.2

        return {
            "temperature_c": random.uniform(24, 38),
            "rainfall_mm": round(rain, 1),
            "wind_speed_kmh": round(random.uniform(5, 35), 1),
            "visibility_km": round(random.uniform(3, 12), 1),
            "storm_alert": storm,
            "description": "simulated data",
            "source": "simulated",
        }


class AQIClient:
    """Air Quality Index — OpenWeather Air Pollution API with simulation fallback"""

    async def get_aqi(self, city: str) -> dict:
        if not settings.OPENWEATHER_API_KEY:
            return self._simulate(city)

        lat, lon = CITY_COORDS.get(city.lower(), (12.9716, 77.5946))
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                r = await client.get(
                    "https://api.openweathermap.org/data/2.5/air_pollution",
                    params={"lat": lat, "lon": lon, "appid": settings.OPENWEATHER_API_KEY},
                )
                r.raise_for_status()
                d = r.json()["list"][0]
                pm25 = d["components"]["pm2_5"]
                aqi_val = d["main"]["aqi"]  # 1–5 OW scale
                # Convert to standard AQI 0–500
                aqi_map = {1: 25, 2: 75, 3: 125, 4: 225, 5: 350}
                return {
                    "aqi": aqi_map.get(aqi_val, 100),
                    "pm25": pm25,
                    "hazardous_alert": aqi_val >= 5,
                    "source": "live",
                }
            except Exception:
                return self._simulate(city)

    def _simulate(self, city: str) -> dict:
        now = datetime.utcnow()
        month = now.month
        # Winter = worse AQI in North India
        is_winter_north = month in (11, 12, 1, 2) and city.lower() in ("delhi", "mumbai")
        aqi = random.randint(200, 350) if is_winter_north else random.randint(60, 160)
        return {
            "aqi": aqi,
            "pm25": round(aqi * 0.35, 1),
            "hazardous_alert": aqi > 300,
            "source": "simulated",
        }


class EconomicDataClient:
    """Fuel price + demand index — with geopolitical stress simulation"""

    BASELINE_FUEL = 102.5  # ₹/liter (Bangalore petrol 2024 avg)

    async def get_economic_data(
        self, city: str, stress_mode: bool = False
    ) -> dict:
        fuel = self.BASELINE_FUEL
        demand_index = 0.85

        if stress_mode:
            # Simulate Iran–Israel conflict → fuel spike + demand drop
            fuel = self.BASELINE_FUEL * random.uniform(1.12, 1.22)
            demand_index = random.uniform(0.45, 0.65)
            geo_stress = random.uniform(0.65, 0.90)
        else:
            fuel = self.BASELINE_FUEL * random.uniform(0.97, 1.06)
            demand_index = random.uniform(0.75, 0.95)
            geo_stress = random.uniform(0.05, 0.25)

        return {
            "fuel_price_per_liter": round(fuel, 2),
            "baseline_fuel_price": self.BASELINE_FUEL,
            "demand_index": round(demand_index, 3),
            "geopolitical_stress": round(geo_stress, 3),
            "fuel_change_pct": round((fuel - self.BASELINE_FUEL) / self.BASELINE_FUEL * 100, 2),
            "source": "simulated",
        }


class PeerDataClient:
    """Peer trend data — aggregated anonymised platform data"""

    async def get_peer_data(self, city: str, stress_mode: bool = False) -> dict:
        baseline_riders = 12000
        baseline_earnings = 850  # ₹/day

        if stress_mode:
            active_today = int(baseline_riders * random.uniform(0.55, 0.70))
            avg_earnings = baseline_earnings * random.uniform(0.45, 0.65)
        else:
            active_today = int(baseline_riders * random.uniform(0.80, 0.95))
            avg_earnings = baseline_earnings * random.uniform(0.80, 1.05)

        return {
            "active_riders_today": active_today,
            "baseline_active_riders": baseline_riders,
            "avg_peer_earnings": round(avg_earnings, 2),
            "baseline_avg_peer_earnings": baseline_earnings,
            "source": "simulated",
        }


# Singletons
weather_client = OpenWeatherClient()
aqi_client = AQIClient()
economic_client = EconomicDataClient()
peer_client = PeerDataClient()
