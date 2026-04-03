import { useState, useEffect, useCallback } from 'react';
import { Users, TrendingUp, AlertTriangle, Zap } from 'lucide-react';
import Topbar from '../components/layout/Topbar';
import StatCard from '../components/ui/StatCard';
import PoolBarChart from '../components/charts/PoolBarChart';
import { fetchAdminDashboard, isUsingMockData } from '../utils/api';
import { useApp } from '../store/AppContext';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const PIE_COLORS = ['#fbbf24', '#f59e0b', '#f43f5e', '#dc2626'];

export default function Admin() {
  const { stressMode, setUsingMock } = useApp();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const r = await fetchAdminDashboard(stressMode);
    setData(r);
    setUsingMock(isUsingMockData());
    setLoading(false);
  }, [stressMode, setUsingMock]);

  useEffect(() => { load(); }, [load]);

  const pool = data?.pool;
  const triggers = data?.trigger_stats;
  const tierDist = data?.payout_tier_distribution;

  const tierPieData = tierDist
    ? Object.entries(tierDist).map(([k, v]) => ({ name: k, value: v }))
    : [];

  return (
    <div className="animate-fade-in">
      <Topbar title="Admin Dashboard" subtitle="Risk pool analytics and trigger monitoring" onRefresh={load} loading={loading} />
      <div className="p-8 space-y-8">

        {/* Pool health */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Pool Balance" value={`₹${((pool?.balance || 0)/100000).toFixed(1)}L`} icon={TrendingUp}
            accent={pool?.health_status === 'healthy' ? 'jade' : 'coral'} loading={loading}
            sub={`Status: ${pool?.health_status || '—'}`} />
          <StatCard label="Active Policies" value={(pool?.active_policies || 0).toLocaleString()} icon={Users}
            accent="teal" loading={loading} sub="Enrolled partners" />
          <StatCard label="Loss Ratio" value={`${pool?.loss_ratio || 0}%`} icon={AlertTriangle}
            accent={pool?.loss_ratio > 60 ? 'coral' : 'amber'} loading={loading}
            sub={`${pool?.loss_ratio > 60 ? 'Elevated — monitor' : 'Within acceptable range'}`} />
          <StatCard label="Reserve Ratio" value={`${pool?.reserve_ratio || 0}%`} icon={Zap}
            accent="slate" loading={loading} sub="Min 20% required" />
        </div>

        {/* Weekly trend */}
        <div className="card-glow">
          <h3 className="section-title mb-5">Premiums vs Payouts — 8-Week Trend</h3>
          {loading ? <div className="h-56 bg-navy-800 rounded-xl animate-pulse" /> : <PoolBarChart data={data?.weekly_trend || []} />}
        </div>

        {/* Triggers + tier dist */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card-glow">
            <h3 className="section-title mb-5">Trigger Analytics (Current Period)</h3>
            <div className="space-y-4">
              {triggers && Object.entries({
                'Weather Triggers': [triggers.weather_triggers, 'teal'],
                'AQI / Pollution': [triggers.aqi_triggers, 'amber'],
                'Demand Drops': [triggers.demand_triggers, 'coral'],
                'Fuel Spikes': [triggers.fuel_triggers, 'jade'],
              }).map(([label, [count, color]]) => {
                const max = Math.max(...Object.values(triggers));
                const pct = Math.round((count / max) * 100);
                const barColors = { teal: 'bg-teal-500', amber: 'bg-amber-500', coral: 'bg-coral-500', jade: 'bg-jade-500' };
                return (
                  <div key={label}>
                    <div className="flex justify-between text-sm mb-1.5">
                      <span className="text-slate-400">{label}</span>
                      <span className="font-mono font-semibold text-slate-200">{count}</span>
                    </div>
                    <div className="h-2 bg-navy-800 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all duration-1000 ${barColors[color]}`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="card-glow">
            <h3 className="section-title mb-4">Payout Tier Distribution</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={tierPieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85}
                  dataKey="value" paddingAngle={4}>
                  {tierPieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                </Pie>
                <Tooltip formatter={(v) => [`${v} payouts`, '']}
                  contentStyle={{ background: '#0c1f3f', border: '1px solid #122952', borderRadius: 12 }}
                  labelStyle={{ color: '#94a3b8' }} />
                <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pool financials table */}
        <div className="card-glow">
          <h3 className="section-title mb-4">Risk Pool Financials</h3>
          <table className="w-full text-sm">
            <tbody>
              {[
                ['Total Collected', `₹${((pool?.total_collected||0)/100000).toFixed(2)}L`, 'text-teal-400'],
                ['Total Paid Out', `₹${((pool?.total_paid_out||0)/100000).toFixed(2)}L`, 'text-coral-400'],
                ['Reserve Fund', `₹${((pool?.reserve||0)/100000).toFixed(2)}L`, 'text-amber-400'],
                ['Net Balance', `₹${((pool?.balance||0)/100000).toFixed(2)}L`, pool?.balance > 0 ? 'text-jade-400' : 'text-coral-400'],
              ].map(([label, val, cls]) => (
                <tr key={label} className="border-b border-navy-800">
                  <td className="py-3 text-slate-400">{label}</td>
                  <td className={`py-3 font-mono font-bold text-right ${cls}`}>{loading ? '—' : val}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
