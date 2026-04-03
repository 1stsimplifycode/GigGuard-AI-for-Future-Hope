"""
GigGuard Risk Pool Manager
Central insurance fund: premiums, payouts, reserves, sustainability
"""

import json
import os
from datetime import datetime, date
from typing import Dict, List
from models.risk_models import RiskTier, WEEKLY_PREMIUMS

POOL_FILE = os.path.join(os.path.dirname(__file__), "../data/risk_pool.json")

RESERVE_RATIO = 0.20  # 20% of pool kept as reserve
MIN_POOL_BALANCE = 50000  # INR — minimum safe balance


class RiskPool:
    def __init__(self):
        self.pool = self._load_or_init()

    def _load_or_init(self) -> dict:
        os.makedirs(os.path.dirname(POOL_FILE), exist_ok=True)
        if os.path.exists(POOL_FILE):
            with open(POOL_FILE) as f:
                return json.load(f)
        return {
            "total_balance": 125000.0,
            "reserve_balance": 25000.0,
            "deployable_balance": 100000.0,
            "total_premiums_collected": 175000.0,
            "total_payouts_made": 50000.0,
            "active_policies": 0,
            "payout_history": [],
            "premium_history": [],
            "last_updated": str(datetime.now()),
        }

    def _save(self):
        os.makedirs(os.path.dirname(POOL_FILE), exist_ok=True)
        with open(POOL_FILE, "w") as f:
            json.dump(self.pool, f, indent=2, default=str)

    def collect_premium(self, partner_id: str, risk_tier: RiskTier, weeks: int = 1) -> dict:
        amount = WEEKLY_PREMIUMS[risk_tier] * weeks
        self.pool["total_balance"] += amount
        self.pool["total_premiums_collected"] += amount
        self.pool["deployable_balance"] = self.pool["total_balance"] * (1 - RESERVE_RATIO)
        self.pool["reserve_balance"] = self.pool["total_balance"] * RESERVE_RATIO
        self.pool["premium_history"].append({
            "partner_id": partner_id,
            "amount": amount,
            "risk_tier": risk_tier.value,
            "date": str(date.today()),
        })
        self.pool["last_updated"] = str(datetime.now())
        self._save()
        return {"collected": amount, "pool_balance": self.pool["total_balance"]}

    def process_payout(self, partner_id: str, amount: float, tier: str) -> dict:
        if amount > self.pool["deployable_balance"]:
            return {"success": False, "reason": "Insufficient deployable balance"}

        self.pool["total_balance"] -= amount
        self.pool["deployable_balance"] = self.pool["total_balance"] * (1 - RESERVE_RATIO)
        self.pool["reserve_balance"] = self.pool["total_balance"] * RESERVE_RATIO
        self.pool["total_payouts_made"] += amount
        self.pool["payout_history"].append({
            "partner_id": partner_id,
            "amount": amount,
            "tier": tier,
            "date": str(date.today()),
        })
        self.pool["last_updated"] = str(datetime.now())
        self._save()
        return {"success": True, "amount_paid": amount, "pool_balance": self.pool["total_balance"]}

    def get_health_metrics(self) -> dict:
        total = self.pool["total_balance"]
        premiums = self.pool["total_premiums_collected"]
        payouts = self.pool["total_payouts_made"]

        loss_ratio = (payouts / premiums * 100) if premiums > 0 else 0
        solvency = (total / MIN_POOL_BALANCE * 100) if MIN_POOL_BALANCE > 0 else 0

        return {
            "total_balance": round(total, 2),
            "reserve_balance": round(self.pool["reserve_balance"], 2),
            "deployable_balance": round(self.pool["deployable_balance"], 2),
            "total_premiums_collected": round(premiums, 2),
            "total_payouts_made": round(payouts, 2),
            "loss_ratio": round(loss_ratio, 2),
            "solvency_ratio": round(min(solvency, 999), 2),
            "pool_health": "HEALTHY" if loss_ratio < 70 and total > MIN_POOL_BALANCE else "WARNING",
            "active_policies": self.pool["active_policies"],
            "recent_payouts": self.pool["payout_history"][-10:],
        }

    def register_policy(self):
        self.pool["active_policies"] += 1
        self._save()

    def deregister_policy(self):
        self.pool["active_policies"] = max(0, self.pool["active_policies"] - 1)
        self._save()


risk_pool = RiskPool()
