import { useState, useEffect } from 'react';
import { Zap, CheckCircle } from 'lucide-react';
import Topbar from '../components/layout/Topbar';
import { fetchPartnerSummary, isUsingMockData } from '../utils/api';
import { useApp } from '../store/AppContext';
import clsx from 'clsx';

const TIER_COLORS = {
  1: 'badge-amber', 2: 'badge-amber', 3: 'badge-coral', 4: 'badge-coral'
};

export default function Payouts() {
  const { setUsingMock } = useApp();
  const [partner, setPartner] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPartnerSummary('GG-2024-04821').then(d => {
      setPartner(d);
      setUsingMock(isUsingMockData());
      setLoading(false);
    });
  }, [setUsingMock]);

  const payouts = partner?.payout_history || [];

  return (
    <div className="animate-fade-in">
      <Topbar title="Payout History" subtitle="Automatic disbursements — no claims required" />
      <div className="p-8 space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="card-glow">
            <div className="stat-label mb-2">Total Payouts Received</div>
            <div className="text-3xl font-mono font-bold text-jade-400">₹{partner?.total_payouts_received?.toLocaleString() || '—'}</div>
          </div>
          <div className="card-glow">
            <div className="stat-label mb-2">Payout Transactions</div>
            <div className="text-3xl font-mono font-bold text-slate-100">{payouts.length}</div>
          </div>
        </div>

        <div className="card-glow">
          <h3 className="section-title mb-5 flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-400" />
            Payout Transactions
          </h3>
          {loading ? (
            <div className="space-y-3">
              {[1,2,3].map(i => <div key={i} className="h-16 bg-navy-800 rounded-xl animate-pulse" />)}
            </div>
          ) : (
            <div className="space-y-3">
              {payouts.map(p => (
                <div key={p.id} className="flex items-center gap-4 px-5 py-4 bg-navy-800/60 border border-navy-700 rounded-xl hover:border-navy-600 transition-colors">
                  <div className="w-10 h-10 rounded-xl bg-jade-500/10 border border-jade-500/25 flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="w-5 h-5 text-jade-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-sm text-slate-100">{p.reason}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{p.id} · {p.date}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`badge ${TIER_COLORS[p.tier] || 'badge-amber'}`}>T{p.tier}</span>
                    <div className="text-right">
                      <div className="font-mono font-bold text-jade-400">₹{p.amount.toLocaleString()}</div>
                      <div className="text-xs text-slate-500">{p.loss_pct}% loss</div>
                    </div>
                    <span className="badge badge-jade">{p.status}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Payout Model Explainer */}
        <div className="card-glow border border-teal-500/15">
          <h3 className="section-title mb-4">How Payouts Work</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-400">
            {[
              { step: '01', title: 'System Detects Loss', desc: 'ARIA monitors weather, AQI, fuel prices, and demand signals in real-time.' },
              { step: '02', title: 'Causation Analysis', desc: 'Algorithm determines whether loss is systemic (external) or individual (excluded).' },
              { step: '03', title: 'Auto Disbursement', desc: 'If eligible, payout is credited automatically — no claim, no paperwork, no delay.' },
            ].map(s => (
              <div key={s.step} className="flex gap-4">
                <div className="text-2xl font-display text-teal-500/30 font-bold flex-shrink-0">{s.step}</div>
                <div>
                  <div className="font-semibold text-slate-200 mb-1">{s.title}</div>
                  <div>{s.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
