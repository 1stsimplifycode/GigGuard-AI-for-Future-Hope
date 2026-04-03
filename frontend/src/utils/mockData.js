// Mock data generator — used when backend is unavailable
// All values are statistically realistic for Indian gig economy

export const generateWorkabilityScore = (stressMode = false) => {
  const base = stressMode ? 32 : 68;
  return Math.max(0, Math.min(100, base + (Math.random() - 0.5) * 20));
};

export const generateEDI = (stressMode = false) => {
  return stressMode
    ? Math.round(200 + Math.random() * 400)
    : Math.round(50 + Math.random() * 150);
};

export const generateCausationScore = (stressMode = false) => {
  return stressMode
    ? parseFloat((0.6 + Math.random() * 0.3).toFixed(3))
    : parseFloat((0.2 + Math.random() * 0.3).toFixed(3));
};

export const generateWeather = (stressMode = false) => ({
  temperature_c: parseFloat((28 + Math.random() * 10).toFixed(1)),
  rainfall_mm: stressMode ? parseFloat((15 + Math.random() * 35).toFixed(1)) : parseFloat((Math.random() * 8).toFixed(1)),
  wind_speed_kmh: parseFloat((10 + Math.random() * 25).toFixed(1)),
  visibility_km: stressMode ? parseFloat((1 + Math.random() * 3).toFixed(1)) : parseFloat((6 + Math.random() * 6).toFixed(1)),
  storm_alert: stressMode && Math.random() > 0.6,
  source: 'simulated',
});

export const generateAQI = (stressMode = false) => {
  const aqi = stressMode ? Math.round(200 + Math.random() * 150) : Math.round(80 + Math.random() * 80);
  return { aqi, pm25: parseFloat((aqi * 0.35).toFixed(1)), hazardous_alert: aqi > 300, source: 'simulated' };
};

export const generateEconomicData = (stressMode = false) => {
  const baseline = 102.5;
  const fuel = stressMode ? baseline * (1.12 + Math.random() * 0.1) : baseline * (0.98 + Math.random() * 0.05);
  const demand = stressMode ? 0.45 + Math.random() * 0.2 : 0.78 + Math.random() * 0.18;
  return {
    fuel_price_per_liter: parseFloat(fuel.toFixed(2)),
    baseline_fuel_price: baseline,
    demand_index: parseFloat(demand.toFixed(3)),
    geopolitical_stress: stressMode ? parseFloat((0.65 + Math.random() * 0.25).toFixed(3)) : parseFloat((Math.random() * 0.2).toFixed(3)),
    fuel_change_pct: parseFloat(((fuel - baseline) / baseline * 100).toFixed(2)),
    source: 'simulated',
  };
};

export const generateEarningsTrend = (days = 30, stressMode = false) =>
  Array.from({ length: days }, (_, i) => {
    const base = 850;
    const stress = stressMode ? 0.55 : 1;
    const actual = base * stress * (0.70 + Math.random() * 0.35);
    const expected = base * (0.92 + Math.random() * 0.12);
    return {
      day: i + 1,
      label: `D${i + 1}`,
      actual_earnings: Math.round(actual),
      expected_earnings: Math.round(expected),
      edi: Math.round(Math.max(0, expected - actual)),
    };
  });

export const generatePayoutHistory = () => [
  { id: 'PYT-001', date: '2024-03-15', amount: 340, tier: 2, loss_pct: 42, reason: 'Heavy rainfall + AQI 210', status: 'processed' },
  { id: 'PYT-002', date: '2024-02-28', amount: 280, tier: 1, loss_pct: 28, reason: 'Demand drop — local strike', status: 'processed' },
  { id: 'PYT-003', date: '2024-02-08', amount: 510, tier: 3, loss_pct: 62, reason: 'Storm alert + fuel spike 14%', status: 'processed' },
  { id: 'PYT-004', date: '2024-01-19', amount: 190, tier: 1, loss_pct: 23, reason: 'Low demand — weekday slump', status: 'processed' },
];

export const generatePoolData = (stressMode = false) => ({
  balance: stressMode ? 1820000 : 3240000,
  total_collected: 4180000,
  total_paid_out: stressMode ? 2360000 : 940000,
  reserve: 500000,
  loss_ratio: stressMode ? 56.5 : 22.5,
  reserve_ratio: stressMode ? 27.5 : 15.4,
  active_policies: 14820,
  health_status: stressMode ? 'stressed' : 'healthy',
});

export const generateWeeklyTrend = (stressMode = false) =>
  Array.from({ length: 8 }, (_, i) => {
    const premiums = 52000 + Math.random() * 22000;
    const basePayouts = stressMode ? 38000 : 12000;
    const payouts = basePayouts + Math.random() * 18000;
    return {
      week: `W${i + 1}`,
      premiums_collected: Math.round(premiums),
      payouts_processed: Math.round(payouts),
      net: Math.round(premiums - payouts),
    };
  });

export const generateCityHeatmap = (stressMode = false) => [
  { city: 'Bengaluru', workability_score: stressMode ? 28 : 65, active_partners: 4820, avg_edi: stressMode ? 310 : 95, payouts_today: stressMode ? 142 : 18 },
  { city: 'Mumbai',    workability_score: stressMode ? 32 : 58, active_partners: 6200, avg_edi: stressMode ? 340 : 110, payouts_today: stressMode ? 198 : 24 },
  { city: 'Delhi',     workability_score: stressMode ? 21 : 44, active_partners: 5500, avg_edi: stressMode ? 420 : 180, payouts_today: stressMode ? 260 : 42 },
  { city: 'Hyderabad', workability_score: stressMode ? 38 : 71, active_partners: 2900, avg_edi: stressMode ? 280 : 80, payouts_today: stressMode ? 98 : 12 },
  { city: 'Chennai',   workability_score: stressMode ? 42 : 72, active_partners: 2200, avg_edi: stressMode ? 250 : 70, payouts_today: stressMode ? 78 : 9 },
  { city: 'Pune',      workability_score: stressMode ? 45 : 74, active_partners: 1800, avg_edi: stressMode ? 220 : 65, payouts_today: stressMode ? 65 : 7 },
];

export const mockPartner = {
  id: 'GG-2024-04821',
  name: 'Ravi Kumar',
  city: 'Bengaluru',
  platform: 'Swiggy',
  risk_level: 'medium',
  weekly_premium: 50,
  policy_active: true,
  total_premiums_paid: 1450,
  total_payouts_received: 1320,
  active_since: '2024-01-15',
};
