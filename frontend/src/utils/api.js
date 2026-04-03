import axios from 'axios';
import * as mock from './mockData';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: BASE_URL, timeout: 6000 });

let usingMockData = false;

export const isUsingMockData = () => usingMockData;

const withFallback = async (fn, fallback) => {
  try {
    const result = await fn();
    usingMockData = false;
    return result;
  } catch {
    usingMockData = true;
    return fallback();
  }
};

export const fetchWorkability = (city = 'bengaluru', stressMode = false) =>
  withFallback(
    async () => {
      const r = await api.get('/api/v1/risk/workability', { params: { city, stress_mode: stressMode } });
      return r.data;
    },
    () => ({
      city, stress_mode: stressMode,
      workability_score: mock.generateWorkabilityScore(stressMode),
      trigger_payout: stressMode,
    })
  );

export const assessRisk = (payload) =>
  withFallback(
    async () => {
      const r = await api.post('/api/v1/risk/assess', payload);
      return r.data;
    },
    () => {
      const stressMode = payload.stress_mode || false;
      const ws = mock.generateWorkabilityScore(stressMode);
      const edi = mock.generateEDI(stressMode);
      const causation = mock.generateCausationScore(stressMode);
      const lossPct = Math.round(edi / payload.expected_earnings * 100);
      const tier = lossPct > 75 ? 4 : lossPct > 55 ? 3 : lossPct > 35 ? 2 : lossPct > 20 ? 1 : null;
      const rateMap = { 1: 0.5, 2: 0.65, 3: 0.75, 4: 0.85 };
      return {
        partner_id: payload.partner_id,
        assessment: {
          workability_score: ws,
          edi,
          causation_score: causation,
          loss_percentage: lossPct,
          is_systemic: causation > 0.4 && ws < 50,
          payout_eligible: stressMode || (causation > 0.4 && ws < 50 && tier !== null),
          payout_tier: tier,
          payout_rate: tier ? rateMap[tier] : null,
          payout_amount: tier ? Math.round(edi * rateMap[tier]) : null,
          exclusion_triggered: false,
          exclusion_reason: null,
          risk_level: ws < 35 ? 'high' : ws < 60 ? 'medium' : 'low',
          weekly_premium: ws < 35 ? 70 : ws < 60 ? 50 : 30,
        },
        causation_breakdown: {
          environment: parseFloat((causation * 0.6).toFixed(3)),
          peer_trend: parseFloat((causation * 0.45).toFixed(3)),
          demand: parseFloat((causation * 0.55).toFixed(3)),
          individual_deviation: 0.05,
        },
        environmental: {
          weather: mock.generateWeather(stressMode),
          aqi: mock.generateAQI(stressMode),
          economic: mock.generateEconomicData(stressMode),
        },
      };
    }
  );

export const fetchEarningsTrend = (partnerId, days = 30, stressMode = false) =>
  withFallback(
    async () => {
      const r = await api.get(`/api/v1/analytics/earnings-trend/${partnerId}`, { params: { days } });
      return r.data;
    },
    () => ({ partner_id: partnerId, trend: mock.generateEarningsTrend(days, stressMode) })
  );

export const fetchPoolSummary = () =>
  withFallback(
    async () => { const r = await api.get('/api/v1/insurance/pool'); return r.data; },
    () => mock.generatePoolData(false)
  );

export const fetchAdminDashboard = (stressMode = false) =>
  withFallback(
    async () => { const r = await api.get('/api/v1/admin/dashboard'); return r.data; },
    () => ({
      pool: mock.generatePoolData(stressMode),
      weekly_trend: mock.generateWeeklyTrend(stressMode),
      trigger_stats: {
        weather_triggers: stressMode ? 340 : 145,
        aqi_triggers: stressMode ? 220 : 92,
        demand_triggers: stressMode ? 480 : 210,
        fuel_triggers: stressMode ? 185 : 67,
      },
      payout_tier_distribution: { T1: 58, T2: 42, T3: 28, T4: 11 },
    })
  );

export const fetchCityHeatmap = (stressMode = false) =>
  withFallback(
    async () => { const r = await api.get('/api/v1/analytics/city-heatmap'); return r.data; },
    () => mock.generateCityHeatmap(stressMode)
  );

export const fetchPartnerSummary = (partnerId) =>
  withFallback(
    async () => { const r = await api.get(`/api/v1/partners/${partnerId}/summary`); return r.data; },
    () => ({ ...mock.mockPartner, payout_history: mock.generatePayoutHistory() })
  );
