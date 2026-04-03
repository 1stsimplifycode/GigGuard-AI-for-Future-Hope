import { useState, useEffect, useCallback } from 'react';
import { Shield, Zap, TrendingDown, Wind, Droplets, Fuel, Activity } from 'lucide-react';
import Topbar from '../components/layout/Topbar';
import StatCard from '../components/ui/StatCard';
import WorkabilityGauge from '../components/ui/WorkabilityGauge';
import CausationRadar from '../components/charts/CausationRadar';
import EarningsTrendChart from '../components/charts/EarningsTrendChart';
import PayoutTierBadge from '../components/ui/PayoutTierBadge';
import { useApp } from '../store/AppContext';
import { assessRisk, fetchEarningsTrend, isUsingMockData } from '../utils/api';
import clsx from 'clsx';

const PARTNER_ID = 'GG-2024-04821';

export default function Dashboard() {
  const { stressMode, setUsingMock, city } = useApp();
  const [data, setData] = useState(null);
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const [riskRes, trendRes] = await Promise.all([
      assessRisk({
        partner_id: PARTNER_ID,
        city,
        actual_earnings: stressMode ? 380 : 720,
        expected_earnings: 850,
        hours_worked: stressMode ? 6 : 9,
        expected_hours: 10,
        voluntary_absence_hours: 0,
        stress_mode: stressMode,
      }),
      fetchEarningsTrend(PARTNER_ID, 30, stressMode),
    ]);
    setData(riskRes);
    setTrend(trendRes.trend || []);
    setUsingMock(isUsingMockData());
    setLoading(false);
  }, [stressMode, city, setUsingMock]);

  useEffect(() => { load(); }, [load]);

  const a = data?.assessment;

  return (
    <div className="animate-fade-in">
      <Topbar
        title="Partner Dashboard"
        subtitle={`GigGuard ID: ${PARTNER_ID} · Bengaluru`}
        onRefresh={load}
        loading={loading}
      />

      <div className="p-8 space-y-8">
        {/* Alert banner when payout eligible */}
        {a?.payout_eligible && (
          <div className="flex items-center gap-4 px-6 py-4 bg-coral-500/10 border border-coral-500/30 rounded-xl animate-slide-up">
            <Zap className="w-5 h-5 text-coral-400 flex-shrink-0 animate-pulse" />
            <div className="flex-1">
              <div className="font-semibold text-coral-300 text-sm">Automatic Payout Triggered</div>
              <div className="text-xs text-coral-400/70 mt-0.5">
                Systemic loss detected. Tier {a.payout_tier} payout of ₹{a.payout_amount?.toLocaleString()} will be credited within 4 hours.
              </div>
            </div>
            <span className="badge badge-coral">Processing</span>
          </div>
        )}

        {/* Stats Row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Workability Score" value={loading ? '—' : Math.round(a?.workability_score || 0)} unit="/100"
            icon={Activity} accent={a?.workability_score < 50 ? 'coral' : 'teal'} loading={loading}
            sub={a?.workability_score < 50 ? 'Payout threshold crossed' : 'Conditions acceptable'} trend={a?.workability_score < 50 ? 'down' : 'up'} />
          <StatCard label="Earnings Deficit (EDI)" value={loading ? '—' : `₹${a?.edi?.toLocaleString() || 0}`}
            icon={TrendingDown} accent="amber" loading={loading}
            sub={`${a?.loss_percentage || 0}% below expected`} trend="down" />
          <StatCard label="Causation Score" value={loading ? '—' : `${((a?.causation_score || 0) * 100).toFixed(0)}%`}
            icon={Shield} accent={a?.causation_score > 0.4 ? 'coral' : 'jade'} loading={loading}
            sub={a?.is_systemic ? 'Systemic loss confirmed' : 'Not systemic'} />
          <StatCard label="Weekly Premium" value={loading ? '—' : `₹${a?.weekly_premium || 50}`}
            icon={Shield} accent="slate" loading={loading}
            sub={`${a?.risk_level || 'medium'} risk tier`} />
        </div>

        {/* Gauge + Environmental */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="card-glow flex flex-col items-center py-6">
            <h3 className="section-title mb-4 self-start">Workability Index</h3>
            <WorkabilityGauge score={a?.workability_score || 0} />
            {a?.workability_score < 50 && (
              <div className="mt-4 w-full px-4 py-3 bg-coral-500/10 border border-coral-500/25 rounded-xl text-center">
                <div className="text-xs text-coral-400 font-semibold">Score below threshold (50)</div>
                <div className="text-xs text-coral-400/60 mt-0.5">Auto-payout trigger activated</div>
              </div>
            )}
          </div>

          <div className="lg:col-span-2 card-glow">
            <h3 className="section-title mb-5">Environmental Conditions</h3>
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: 'AQI', value: data?.environmental?.aqi?.aqi || '—', icon: Wind,
                  color: (data?.environmental?.aqi?.aqi || 0) > 200 ? 'text-coral-400' : 'text-jade-400',
                  sub: (data?.environmental?.aqi?.aqi || 0) > 200 ? 'Hazardous' : 'Moderate' },
                { label: 'Rainfall', value: `${data?.environmental?.weather?.rainfall_mm || 0} mm`, icon: Droplets,
                  color: (data?.environmental?.weather?.rainfall_mm || 0) > 10 ? 'text-amber-400' : 'text-teal-400',
                  sub: data?.environmental?.weather?.storm_alert ? 'Storm Alert!' : 'Normal' },
                { label: 'Fuel Price', value: `₹${data?.environmental?.economic?.fuel_price_per_liter || '—'}`, icon: Fuel,
                  color: (data?.environmental?.economic?.fuel_change_pct || 0) > 5 ? 'text-coral-400' : 'text-jade-400',
                  sub: `${data?.environmental?.economic?.fuel_change_pct > 0 ? '+' : ''}${data?.environmental?.economic?.fuel_change_pct || 0}% vs baseline` },
                { label: 'Demand Index', value: `${((data?.environmental?.economic?.demand_index || 1) * 100).toFixed(0)}%`, icon: Activity,
                  color: (data?.environmental?.economic?.demand_index || 1) < 0.6 ? 'text-coral-400' : 'text-teal-400',
                  sub: stressMode ? 'Severely depressed' : 'Normal demand' },
              ].map(item => (
                <div key={item.label} className="bg-navy-800/60 rounded-xl p-4 border border-navy-700">
                  <div className="flex items-center gap-2 mb-2">
                    <item.icon className="w-4 h-4 text-slate-500" />
                    <span className="stat-label">{item.label}</span>
                  </div>
                  <div className={clsx('text-2xl font-mono font-bold', item.color)}>{item.value}</div>
                  <div className="text-xs text-slate-500 mt-1">{item.sub}</div>
                </div>
              ))}
            </div>
            {stressMode && (
              <div className="mt-4 text-xs text-amber-400/80 flex items-center gap-2 px-3 py-2 bg-amber-500/5 rounded-lg border border-amber-500/15">
                <span className="font-semibold">Geopolitical Stress:</span>
                {((data?.environmental?.economic?.geopolitical_stress || 0) * 100).toFixed(0)}% — Iran–Israel conflict simulation active
              </div>
            )}
          </div>
        </div>

        {/* Payout Tiers */}
        <div className="card-glow">
          <h3 className="section-title mb-5">Payout Tier Structure</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(t => (
              <PayoutTierBadge
                key={t}
                tier={t}
                active={a?.payout_tier === t}
                amount={a?.payout_tier === t ? a?.payout_amount : null}
              />
            ))}
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 card-glow">
            <h3 className="section-title mb-5">30-Day Earnings Trend</h3>
            <EarningsTrendChart data={trend} loading={loading} />
          </div>
          <CausationRadar data={data?.causation_breakdown} />
        </div>
      </div>
    </div>
  );
}
