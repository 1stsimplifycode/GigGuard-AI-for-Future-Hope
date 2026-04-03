"""
GigGuard Insurance Engine
Risk Pool Management, Premium Collection, Payout Processing
"""
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from core.config import settings


@dataclass
class PolicyHolder:
    id: str
    name: str
    phone: str
    platform: str  # swiggy / zomato / dunzo / other
    city: str
    risk_level: str
    weekly_premium: int
    policy_start: datetime
    policy_active: bool = True
    total_premiums_paid: float = 0.0
    total_payouts_received: float = 0.0


@dataclass
class PremiumTransaction:
    id: str
    partner_id: str
    amount: float
    week_start: datetime
    week_end: datetime
    collected_at: datetime
    status: str  # collected / failed / waived


@dataclass
class PayoutTransaction:
    id: str
    partner_id: str
    amount: float
    tier: int
    payout_rate: float
    edi: float
    loss_percentage: float
    workability_score: float
    causation_score: float
    trigger_reason: str
    processed_at: datetime
    status: str  # processed / pending / rejected


@dataclass
class RiskPool:
    total_collected: float = 0.0
    total_paid_out: float = 0.0
    reserve: float = 0.0
    active_policies: int = 0

    @property
    def balance(self) -> float:
        return self.total_collected - self.total_paid_out + self.reserve

    @property
    def loss_ratio(self) -> float:
        if self.total_collected == 0:
            return 0.0
        return self.total_paid_out / self.total_collected

    @property
    def reserve_ratio(self) -> float:
        if self.balance == 0:
            return 0.0
        return self.reserve / self.balance


class InsuranceEngine:
    """
    GigGuard Insurance Engine — manages the risk pool, premiums, and payouts
    """

    def __init__(self):
        self.pool = RiskPool(reserve=settings.INITIAL_RESERVE)
        self.premium_history: List[PremiumTransaction] = []
        self.payout_history: List[PayoutTransaction] = []
        self.partners: Dict[str, PolicyHolder] = {}

    def enroll_partner(
        self,
        name: str,
        phone: str,
        platform: str,
        city: str,
        risk_level: str,
    ) -> PolicyHolder:
        premium_map = {
            "low": settings.PREMIUM_LOW_RISK,
            "medium": settings.PREMIUM_MEDIUM_RISK,
            "high": settings.PREMIUM_HIGH_RISK,
        }
        partner = PolicyHolder(
            id=str(uuid.uuid4()),
            name=name,
            phone=phone,
            platform=platform,
            city=city,
            risk_level=risk_level,
            weekly_premium=premium_map.get(risk_level, settings.PREMIUM_MEDIUM_RISK),
            policy_start=datetime.utcnow(),
        )
        self.partners[partner.id] = partner
        self.pool.active_policies += 1
        return partner

    def collect_premium(self, partner_id: str) -> Optional[PremiumTransaction]:
        partner = self.partners.get(partner_id)
        if not partner or not partner.policy_active:
            return None

        now = datetime.utcnow()
        tx = PremiumTransaction(
            id=str(uuid.uuid4()),
            partner_id=partner_id,
            amount=partner.weekly_premium,
            week_start=now,
            week_end=now + timedelta(days=7),
            collected_at=now,
            status="collected",
        )
        self.pool.total_collected += partner.weekly_premium
        partner.total_premiums_paid += partner.weekly_premium
        self.premium_history.append(tx)
        return tx

    def process_payout(
        self,
        partner_id: str,
        edi: float,
        loss_percentage: float,
        tier: int,
        payout_rate: float,
        workability_score: float,
        causation_score: float,
        trigger_reason: str,
    ) -> Optional[PayoutTransaction]:
        partner = self.partners.get(partner_id)
        if not partner or not partner.policy_active:
            return None

        payout_amount = edi * payout_rate

        # Reserve check
        if self.pool.balance - payout_amount < self.pool.balance * settings.RESERVE_RATIO:
            trigger_reason += " [PARTIAL — reserve constraint]"
            payout_amount *= 0.5

        tx = PayoutTransaction(
            id=str(uuid.uuid4()),
            partner_id=partner_id,
            amount=round(payout_amount, 2),
            tier=tier,
            payout_rate=payout_rate,
            edi=edi,
            loss_percentage=loss_percentage,
            workability_score=workability_score,
            causation_score=causation_score,
            trigger_reason=trigger_reason,
            processed_at=datetime.utcnow(),
            status="processed",
        )
        self.pool.total_paid_out += payout_amount
        partner.total_payouts_received += payout_amount
        self.payout_history.append(tx)
        return tx

    def get_pool_summary(self) -> dict:
        return {
            "balance": round(self.pool.balance, 2),
            "total_collected": round(self.pool.total_collected, 2),
            "total_paid_out": round(self.pool.total_paid_out, 2),
            "reserve": round(self.pool.reserve, 2),
            "loss_ratio": round(self.pool.loss_ratio * 100, 2),
            "reserve_ratio": round(self.pool.reserve_ratio * 100, 2),
            "active_policies": self.pool.active_policies,
            "is_solvent": self.pool.balance > 0,
            "health_status": self._pool_health(),
        }

    def _pool_health(self) -> str:
        lr = self.pool.loss_ratio
        if lr < 0.5:
            return "healthy"
        elif lr < 0.75:
            return "moderate"
        elif lr < 1.0:
            return "stressed"
        return "critical"


# Singleton
insurance_engine = InsuranceEngine()
