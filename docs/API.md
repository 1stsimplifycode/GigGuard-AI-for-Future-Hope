# ARIA-Gig / GigGuard — API Documentation

Base URL: `https://your-backend.railway.app`  
Interactive docs: `/docs` (Swagger UI) | `/redoc` (ReDoc)

---

## Authentication
Currently open (add Bearer token for production).

---

## Risk Engine

### POST `/api/v1/risk/assess`
Full risk assessment for a delivery partner.

**Request:**
```json
{
  "partner_id": "P001",
  "risk_tier": "medium",
  "economic_stress_mode": false,
  "weather": {
    "temperature": 32.5,
    "wind_speed": 18.0,
    "precipitation": 0.0,
    "visibility": 9.0,
    "condition": "Clear",
    "aqi": 95.0
  },
  "market": {
    "fuel_price_per_liter": 99.5,
    "fuel_baseline": 96.0,
    "demand_index": 0.82,
    "peer_earnings_trend": -0.05,
    "platform_demand_change": -0.03
  },
  "earnings": {
    "partner_id": "P001",
    "expected_daily": 750.0,
    "actual_daily": 580.0,
    "hours_worked": 8.5,
    "orders_completed": 14,
    "voluntary_absence": false,
    "platform_banned": false,
    "vehicle_failure": false
  }
}
```

**Response:**
```json
{
  "partner_id": "P001",
  "workability": {
    "score": 72.4,
    "trigger_payout": false,
    "breakdown": { "temperature": 0, "wind": -3.0, "precipitation": 0, "aqi": -5.0, "fuel_price": -4.0, "demand": -3.0 }
  },
  "edi": {
    "expected_earnings": 750.0,
    "actual_earnings": 580.0,
    "edi_absolute": 170.0,
    "edi_percentage": 22.67,
    "loss_pct": 0.2267
  },
  "causation": {
    "causation_score": 0.3812,
    "is_systemic": false,
    "breakdown": { "env_weighted": 0.12, "peer_weighted": 0.06, "demand_weighted": 0.09, "individual_penalty": -0.04 }
  },
  "payout": {
    "eligible": false,
    "tier": "NONE",
    "reason": "No systemic trigger detected"
  },
  "risk_tier": "medium",
  "timestamp": "2024-12-02T14:30:00",
  "stress_mode_active": false
}
```

---

### GET `/api/v1/risk/workability?city=Bangalore,IN&stress_mode=false`
Live workability score with real-time weather data.

---

### GET `/api/v1/risk/stress-test?partner_id=P001`
Simulate geopolitical economic stress scenario.

---

### GET `/api/v1/risk/payout-tiers`
Returns tier configuration, premiums, coverage rules.

---

## Policy

### GET `/api/v1/policy/{partner_id}`
```json
{
  "partner_id": "P001",
  "policy_number": "GG-P001-2024",
  "status": "active",
  "risk_tier": "medium",
  "weekly_premium": 50,
  "total_premiums_paid": 650,
  "total_payouts_received": 745,
  "claims_count": 3
}
```

### GET `/api/v1/policy/{partner_id}/history`
Weekly premium and payout history.

---

## Admin

### GET `/api/v1/admin/pool`
```json
{
  "total_balance": 125000.0,
  "reserve_balance": 25000.0,
  "deployable_balance": 100000.0,
  "total_premiums_collected": 175000.0,
  "total_payouts_made": 50000.0,
  "loss_ratio": 28.57,
  "solvency_ratio": 250.0,
  "pool_health": "HEALTHY",
  "active_policies": 847
}
```

### GET `/api/v1/admin/summary`
Full admin summary with partner counts and system status.

---

## Analytics

### GET `/api/v1/analytics/dashboard`
12-week premium vs payout trend data.

### GET `/api/v1/analytics/triggers`
Trigger source breakdown (Workability vs Causation) and tier distribution.

---

## Payout

### GET `/api/v1/payout/{partner_id}/history`
```json
{
  "partner_id": "P001",
  "payouts": [
    { "date": "2024-12-02", "amount": 245, "tier": "T2", "reason": "Heavy rainfall — Workability 38" },
    { "date": "2024-11-18", "amount": 180, "tier": "T1", "reason": "High AQI 215 — Causation 0.72" }
  ],
  "total": 745
}
```

---

## Error Responses
```json
{ "detail": "Error message", "status_code": 400 }
```

Common codes: `400` Bad Request | `404` Not Found | `500` Internal Error
