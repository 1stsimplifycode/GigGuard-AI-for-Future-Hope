import { useState, useEffect } from 'react';
import Topbar from '../components/layout/Topbar';
import { fetchPoolSummary, isUsingMockData } from '../utils/api';
import { useApp } from '../store/AppContext';
import clsx from 'clsx';

export default function RiskPool() {
  const { setUsingMock } = useApp();
  const [pool, setPool] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPoolSummary().then(d => { setPool(d); setUsingMock(isUsingMockData()); setLoading(false); });
  }, [setUsingMock]);

  const healthColor = { healthy: 'text-jade-400', moderate: 'text-amber-400', stressed: 'text-coral-400', critical: 'text-red-400' };

  return (
    <div className="animate-fade-in">
      <Topbar title="Risk Pool" subtitle="Central insurance fund management" />
      <div className="p-8 space-y-6">
        <div className="card-glow border border-teal-500/15">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="font-display text-3xl text-slate-100">GigGuard Central Risk Pool</h2>
              <p className="text-slate-500 text-sm mt-1">Collectively managed insurance fund for all enrolled delivery partners</p>
            </div>
            <div className="text-right">
              <div className="stat-label">Pool Health</div>
              <div className={clsx('text-2xl font-bold capitalize', healthColor[pool?.health_status] || 'text-slate-300')}>
                {pool?.health_status || '—'}
              </div>
            </div>
          </div>

          {/* Balance meter */}
          <div className="mb-6">
            <div className="flex justify-between text-xs text-slate-500 mb-2">
              <span>Pool Utilisation</span>
              <span>{pool?.loss_ratio || 0}%</span>
            </div>
            <div className="h-3 bg-navy-800 rounded-full overflow-hidden">
              <div
                className={clsx('h-full rounded-full transition-all duration-1000',
                  (pool?.loss_ratio || 0) > 70 ? 'bg-coral-500' : (pool?.loss_ratio || 0) > 45 ? 'bg-amber-500' : 'bg-teal-500'
                )}
                style={{ width: `${Math.min(100, pool?.loss_ratio || 0)}%` }}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Net Balance', value: `₹${((pool?.balance||0)/100000).toFixed(1)}L`, color: 'text-jade-400' },
              { label: 'Total Collected', value: `₹${((pool?.total_collected||0)/100000).toFixed(1)}L`, color: 'text-teal-400' },
              { label: 'Total Paid Out', value: `₹${((pool?.total_paid_out||0)/100000).toFixed(1)}L`, color: 'text-coral-400' },
              { label: 'Reserve Fund', value: `₹${((pool?.reserve||0)/100000).toFixed(1)}L`, color: 'text-amber-400' },
            ].map(f => (
              <div key={f.label} className="bg-navy-800/60 rounded-xl p-4 border border-navy-700">
                <div className="stat-label mb-2">{f.label}</div>
                <div className={clsx('text-2xl font-mono font-bold', f.color)}>{loading ? '—' : f.value}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Premium model */}
        <div className="card-glow">
          <h3 className="section-title mb-5">Weekly Premium Model</h3>
          <div className="grid grid-cols-3 gap-4">
            {[
              { tier: 'Low Risk', premium: '₹30', color: 'border-jade-500/30 bg-jade-500/05 text-jade-400', desc: 'Workability > 70, Causation < 0.3' },
              { tier: 'Medium Risk', premium: '₹50', color: 'border-amber-500/30 bg-amber-500/05 text-amber-400', desc: 'Workability 50–70, Causation 0.3–0.5' },
              { tier: 'High Risk', premium: '₹70', color: 'border-coral-500/30 bg-coral-500/05 text-coral-400', desc: 'Workability < 50, Causation > 0.5' },
            ].map(p => (
              <div key={p.tier} className={clsx('border rounded-xl p-5', p.color)}>
                <div className="text-xs uppercase tracking-widest mb-2 opacity-70">{p.tier}</div>
                <div className="text-3xl font-mono font-bold">{p.premium}</div>
                <div className="text-xs opacity-60 mt-1">per week</div>
                <div className="text-xs opacity-50 mt-3">{p.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Reserve rules */}
        <div className="card-glow">
          <h3 className="section-title mb-4">Reserve Policy</h3>
          <div className="space-y-3 text-sm text-slate-400">
            <div className="flex gap-4 p-4 bg-navy-800/50 rounded-xl">
              <div className="font-mono font-bold text-teal-400 w-16 flex-shrink-0">20%</div>
              <div>Minimum reserve ratio maintained at all times. Payouts are partially constrained if reserve falls below this threshold.</div>
            </div>
            <div className="flex gap-4 p-4 bg-navy-800/50 rounded-xl">
              <div className="font-mono font-bold text-amber-400 w-16 flex-shrink-0">₹5L</div>
              <div>Seed reserve funded at pool inception. Acts as buffer during initial low-premium high-payout periods.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
