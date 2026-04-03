"""Seed database with initial data"""
import os, json

def seed_database():
    data_dir = os.path.join(os.path.dirname(__file__), "../data")
    os.makedirs(data_dir, exist_ok=True)
    pool_file = os.path.join(data_dir, "risk_pool.json")
    if not os.path.exists(pool_file):
        with open(pool_file, "w") as f:
            json.dump({
                "total_balance": 125000.0,
                "reserve_balance": 25000.0,
                "deployable_balance": 100000.0,
                "total_premiums_collected": 175000.0,
                "total_payouts_made": 50000.0,
                "active_policies": 847,
                "payout_history": [],
                "premium_history": [],
                "last_updated": "2024-01-01T00:00:00",
            }, f, indent=2)
