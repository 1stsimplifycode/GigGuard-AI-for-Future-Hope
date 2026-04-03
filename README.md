# ARIA-Gig / GigGuard
## Invisible Loss Insurance for Delivery Partners

> Automatically detecting and compensating gig workers for income lost due to weather, pollution, demand collapse, and fuel price spikes — without claims, without delays.

---

## 🎯 Problem Statement

Delivery partners on Swiggy, Zomato, and similar platforms suffer daily **invisible income loss** from:

| Factor | Impact | Traditional Insurance |
|--------|--------|----------------------|
| Heavy rainfall | Unrideable hours, lost orders | ❌ Not covered |
| High AQI/Pollution | Health risk, forced stops | ❌ Not covered |
| Demand fluctuations | Platform-level order collapse | ❌ Not covered |
| Fuel price spikes | Eroded margins | ❌ Not covered |
| Geopolitical effects | Iran-Israel → oil prices → fuel → demand | ❌ Not covered |

**GigGuard solves this with parametric, automatic compensation.**

---

## 🧠 Core Models

### 1. Workability Index (0–100)
```
Score = 100 - WeatherPenalty - AQIPenalty - FuelPenalty - DemandPenalty
Trigger: Score < 50 → Payout eligible
```

### 2. Earnings Deficit Index (EDI)
```
EDI = Expected Daily Earnings − Actual Daily Earnings
EDI% = (EDI / Expected) × 100
```

### 3. Causation Model
```
Causation = 0.40 × Environment
          + 0.30 × Peer Trends
          + 0.30 × Demand
          − 0.25 × Individual Deviation

Score > 0.60 → Systemic loss → Payout eligible
```

### 4. Payout Tiers
| Tier | Loss Range | Payout Rate |
|------|-----------|-------------|
| T1   | 20–35%    | 50% of deficit |
| T2   | 35–55%    | 65% of deficit |
| T3   | 55–75%    | 75% of deficit |
| T4   | 75–100%   | 85% of deficit |

### 5. Weekly Premiums
| Risk Tier | Weekly | Monthly |
|-----------|--------|---------|
| Low       | ₹30    | ₹120   |
| Medium    | ₹50    | ₹200   |
| High      | ₹70    | ₹280   |

---

## 📁 Project Structure

```
aria-gig/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── requirements.txt
│   ├── models/
│   │   └── risk_models.py         # Pydantic data models
│   ├── routers/
│   │   ├── risk.py                # Risk assessment endpoints
│   │   ├── policy.py              # Policy management
│   │   ├── analytics.py           # Dashboard analytics
│   │   ├── admin.py               # Admin pool management
│   │   └── payout.py              # Payout history
│   ├── services/
│   │   ├── risk_engine.py         # ⭐ Core risk computation
│   │   ├── external_apis.py       # Weather + market data
│   │   └── risk_pool.py           # Insurance fund management
│   └── utils/
│       └── seed_data.py           # Database seeding
├── frontend/
│   └── src/                       # React 18 + Vite
├── docs/
│   └── API.md                     # Full API documentation
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
# Add your OPENWEATHER_API_KEY to .env
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend (React + Vite)

```bash
cd frontend
npm install
cp ../.env.example .env.local
# Set VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

---

## 🌐 Deployment

### Backend → Railway / Render

```bash
# railway.toml
[build]
  builder = "NIXPACKS"
  buildCommand = "pip install -r requirements.txt"

[deploy]
  startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

Environment variables to set:
- `OPENWEATHER_API_KEY`
- `ENVIRONMENT=production`

### Frontend → Vercel

```bash
npm i -g vercel
cd frontend
vercel --prod
```

Set in Vercel dashboard:
- `VITE_API_BASE_URL` = your Railway/Render URL

---

## 📡 Key API Endpoints

```
POST /api/v1/risk/assess           # Full risk assessment
GET  /api/v1/risk/workability      # Live workability score
GET  /api/v1/risk/stress-test      # Economic stress simulation
GET  /api/v1/risk/payout-tiers     # Tier configuration
GET  /api/v1/policy/{id}           # Partner policy details
GET  /api/v1/admin/pool            # Risk pool health
GET  /api/v1/analytics/dashboard   # Weekly analytics
```

---

## 🌍 Economic Stress Mode

Toggle **High Economic Stress Mode** to simulate geopolitical disruption:

- Fuel prices surge 15–25% (Iran-Israel conflict simulation)
- Order demand drops 30–35% 
- AQI increases 30% (less rain, more dust)
- Workability Score drops below 42
- Causation score rises above 0.75
- T3/T4 payouts auto-trigger

---

## 🛡️ Coverage Rules

**Covered:**
- Income loss from weather/AQI/demand/fuel spikes (systemic)

**Excluded:**
- Voluntary platform absence
- Platform ban/deactivation
- Vehicle mechanical failure
- Direct war damage
- Direct pandemic illness (economic effects covered)

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, NumPy, Pandas |
| Frontend | React 18, Recharts, Tailwind CSS, Lucide |
| Weather API | OpenWeatherMap (with realistic fallback) |
| Deployment | Railway (backend), Vercel (frontend) |
| Data | JSON file store (upgradeable to PostgreSQL) |

---

## 📄 License

MIT © ARIA-Gig / GigGuard 2024
