# ARIA-Gig / GigGuard — Deployment Guide

## 1. Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend
```bash
git clone https://github.com/your-org/aria-gig.git
cd aria-gig/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env → add OPENWEATHER_API_KEY
uvicorn main:app --reload --port 8000
# → API at http://localhost:8000
# → Docs at http://localhost:8000/docs
```

### Frontend
```bash
cd aria-gig/frontend
npm install
cp ../.env.example .env.local
# Edit .env.local → VITE_API_BASE_URL=http://localhost:8000
npm run dev
# → UI at http://localhost:3000
```

### Run Tests
```bash
cd backend
python -m pytest tests/ -v
```

---

## 2. Production — Railway (Backend)

1. Push to GitHub
2. Create Railway account → New Project → Deploy from GitHub
3. Select `backend/` as root directory
4. Set environment variables:
   - `OPENWEATHER_API_KEY` = your key
   - `ENVIRONMENT` = production
5. Railway auto-detects Dockerfile → deploys
6. Copy the Railway URL (e.g. `https://aria-gig-api.railway.app`)

---

## 3. Production — Vercel (Frontend)

1. Install Vercel CLI: `npm i -g vercel`
2. In `frontend/`:
   ```bash
   vercel
   # Follow prompts
   ```
3. Set environment variable in Vercel dashboard:
   - `VITE_API_BASE_URL` = Railway URL from step 2
4. Redeploy: `vercel --prod`

---

## 4. Frontend Resilience

If the backend is unavailable:
- Frontend auto-detects on startup (5s timeout)
- Falls back to generated data automatically
- Shows: "Live data unavailable — showing generated data"
- All dashboards remain fully functional

---

## 5. Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENWEATHER_API_KEY` | Optional | Weather + AQI data. Falls back to simulation if missing. |
| `ENVIRONMENT` | No | `development` or `production` |
| `PORT` | No | Backend port (Railway sets automatically) |
| `VITE_API_BASE_URL` | Yes (frontend) | Backend URL |

---

## 6. Docker (Self-hosted)

```bash
# Backend
cd backend
docker build -t aria-gig-api .
docker run -p 8000:8000 \
  -e OPENWEATHER_API_KEY=your_key \
  aria-gig-api

# Frontend (static build)
cd frontend
npm run build
npx serve dist -p 3000
```

---

## 7. Monitoring

Health endpoint: `GET /health`
```json
{ "status": "healthy", "uptime": "operational" }
```

Pool metrics: `GET /api/v1/admin/pool`
