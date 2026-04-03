"""
Core Configuration — ARIA-Gig Backend
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ARIA-Gig"
    APP_ENV: str = "production"
    DEBUG: bool = False
    SECRET_KEY: str = "aria-gig-secret-change-in-production"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://aria-gig.vercel.app",
    ]

    # External APIs
    OPENWEATHER_API_KEY: str = ""
    YELP_API_KEY: str = ""
    HAZARDHUB_API_KEY: str = ""

    # Database (PostgreSQL for production, SQLite for dev)
    DATABASE_URL: str = "sqlite:///./aria_gig.db"

    # Redis (for caching)
    REDIS_URL: str = "redis://localhost:6379"

    # Insurance Parameters
    PREMIUM_LOW_RISK: int = 30          # ₹30/week
    PREMIUM_MEDIUM_RISK: int = 50       # ₹50/week
    PREMIUM_HIGH_RISK: int = 70         # ₹70/week

    # Risk Pool
    INITIAL_RESERVE: float = 500000.0   # ₹5 lakh seed reserve
    RESERVE_RATIO: float = 0.20         # 20% minimum reserve

    # Payout Tiers
    PAYOUT_TIER_1_MIN: float = 0.20    # 20% loss
    PAYOUT_TIER_1_MAX: float = 0.35
    PAYOUT_TIER_1_RATE: float = 0.50

    PAYOUT_TIER_2_MIN: float = 0.35
    PAYOUT_TIER_2_MAX: float = 0.55
    PAYOUT_TIER_2_RATE: float = 0.65

    PAYOUT_TIER_3_MIN: float = 0.55
    PAYOUT_TIER_3_MAX: float = 0.75
    PAYOUT_TIER_3_RATE: float = 0.75

    PAYOUT_TIER_4_MIN: float = 0.75
    PAYOUT_TIER_4_MAX: float = 1.00
    PAYOUT_TIER_4_RATE: float = 0.85

    # Workability threshold
    WORKABILITY_PAYOUT_THRESHOLD: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
