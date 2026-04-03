import { useState, useEffect, useCallback } from 'react';
import { MapPin, TrendingDown, Users, Zap } from 'lucide-react';
import Topbar from '../components/layout/Topbar';
import { fetchCityHeatmap, isUsingMockData } from '../utils/api';
import { useApp } from '../store/AppContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import clsx from 'clsx';

export default function Heatmap() {
  const { stressMode, setUsingMock } = useApp();
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const r = await fetchCityHeatmap(stressMode);
    setCities(r);
    setUsingMock(isUsingMockData());
    setLoading(false);
  }, [stressMode, setUsingMock]);

  useEffect(() => { load(); }, [load]);

  const scoreColor = (s) => s >= 70 ? 'text-jade-400' : s >= 50 ? 'text-amber-400' : 'text-coral-400';
  const scoreBg   = (s) => s >= 70 ? 'bg-jade-500'  : s >= 50 ? 'bg-amber-500'  : 'bg-coral-500';

  return (
    <div className="animate-fade-in">
      <Topbar title="City Heatmap" subtitle="Real-time workability across metro cities" onRefresh={load} loading={loading} />
      <div className="p-8 space-y-6">

        {/* City cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(loading ? Array(6).fill(null) : cities).map((city, i) => (
            <div key={i} className={clsx('card-glow', loading && 'animate-pulse')}>
              {loading ? (
                <div className="h-32 bg-navy-800 rounded-xl" />
              ) : (
                <>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-slate-500" />
                      <span className="font-semibold text-slate-100">{city.city}</span>
                    </div>
                    <span className={clsx('badge', city.workability_score >= 70 ? 'badge-jade' : city.workability_score >= 50 ? 'badge-amber' : 'badge-coral')}>
                      {city.workability_score >= 70 ? 'Clear' : city.workability_score >= 50 ? 'Caution' : 'At Risk'}
                    </span>
                  </div>

                  {/* Score bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="text-slate-500">Workability</span>
                      <span className={clsx('font-mono font-bold', scoreColor(city.workability_score))}>{city.workability_score}</span>
                    </div>
                    <div className="h-2 bg-navy-800 rounded-full overflow-hidden">
                      <div className={clsx('h-full rounded-full transition-all duration-1000', scoreBg(city.workability_score))}
                        style={{ width: `${city.workability_score}%` }} />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center">
                    {[
                      { label: 'Partners', value: city.active_partners?.toLocaleString(), icon: Users },
                      { label: 'Avg EDI', value: `₹${city.avg_edi}`, icon: TrendingDown },
                      { label: 'Payouts', value: city.payouts_today, icon: Zap },
                    ].map(f => (
                      <div key={f.label} className="bg-navy-800/60 rounded-lg p-2.5">
                        <div className="text-xs text-slate-500 mb-1">{f.label}</div>
                        <div className="font-mono font-semibold text-sm text-slate-200">{f.value}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>

        {/* City comparison chart */}
        <div className="card-glow">
          <h3 className="section-title mb-5">Workability Score Comparison</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={cities} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="city" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: '#0c1f3f', border: '1px solid #122952', borderRadius: 12, fontSize: 12 }}
                labelStyle={{ color: '#94a3b8' }}
              />
              <Bar dataKey="workability_score" name="Workability Score" radius={[6, 6, 0, 0]}>
                {cities.map((c, i) => (
                  <rect key={i} fill={c.workability_score >= 70 ? '#22c55e' : c.workability_score >= 50 ? '#fbbf24' : '#f43f5e'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* EDI comparison */}
        <div className="card-glow">
          <h3 className="section-title mb-5">Average Earnings Deficit Index by City</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={cities} layout="vertical" margin={{ top: 5, right: 20, left: 60, bottom: 5 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `₹${v}`} />
              <YAxis type="category" dataKey="city" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: '#0c1f3f', border: '1px solid #122952', borderRadius: 12, fontSize: 12 }}
                formatter={(v) => [`₹${v}`, 'Avg EDI']}
              />
              <Bar dataKey="avg_edi" name="Avg EDI" fill="#f59e0b" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
