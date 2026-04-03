import { useState, useEffect } from 'react';
import { Shield, CheckCircle, XCircle, Calendar, IndianRupee } from 'lucide-react';
import Topbar from '../components/layout/Topbar';
import { fetchPartnerSummary, isUsingMockData } from '../utils/api';
import { useApp } from '../store/AppContext';
import clsx from 'clsx';

const INCLUSIONS = [
  'Income loss due to weather disruptions (rain, storm, fog)',
  'Earnings deficit caused by AQI/pollution alerts',
  'Demand drops due to economic or geopolitical events',
  'Fuel price spike-induced profitability loss',
  'Indirect income loss from Iran–Israel or global supply shocks',
];

const EXCLUSIONS = [
  'Voluntary absence or self-imposed work stoppage',
  'Platform ban or account suspension',
  'Vehicle breakdown or mechanical failure',
  'Direct war zone damage',
  'Pandemic-direct-cause income loss',
];

export default function Policy() {
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

  return (
    <div className="animate-fade-in">
      <Topbar title="My Policy" subtitle="GigGuard™ Invisible Loss Coverage" />
      <div className="p-8 space-y-6">
        {/* Policy Card */}
        <div className="card-glow border border-teal-500/20 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 rounded-full bg-teal-500/03 blur-3xl pointer-events-none" />
          <div className="flex flex-col md:flex-row md:items-start gap-6">
            <div className="w-16 h-16 rounded-2xl bg-teal-500/15 border border-teal-500/30 flex items-center justify-center flex-shrink-0">
              <Shield className="w-8 h-8 text-teal-400" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 flex-wrap">
                <h2 className="font-display text-2xl text-slate-100">GigGuard Invisible Loss Cover</h2>
                <span className="badge badge-jade">Active</span>
              </div>
              <p className="text-sm text-slate-400 mt-1">Policy ID: {partner?.id || 'GG-2024-04821'}</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-5">
                {[
                  { label: 'Partner', value: partner?.name || 'Ravi Kumar', icon: null },
                  { label: 'Platform', value: partner?.platform || 'Swiggy', icon: null },
                  { label: 'Risk Tier', value: partner?.risk_level || 'medium', icon: null },
                  { label: 'Active Since', value: partner?.active_since || '2024-01-15', icon: null },
                ].map(f => (
                  <div key={f.label}>
                    <div className="stat-label mb-1">{f.label}</div>
                    <div className="font-semibold text-slate-200 capitalize">{f.value}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="text-right flex-shrink-0">
              <div className="stat-label">Weekly Premium</div>
              <div className="text-3xl font-mono font-bold text-teal-400 mt-1">₹{partner?.weekly_premium || 50}</div>
              <div className="text-xs text-slate-500 mt-0.5">auto-deducted</div>
            </div>
          </div>
        </div>

        {/* Premium stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="card-glow">
            <div className="stat-label mb-2">Total Premiums Paid</div>
            <div className="text-3xl font-mono font-bold text-slate-100">₹{partner?.total_premiums_paid?.toLocaleString() || '—'}</div>
          </div>
          <div className="card-glow">
            <div className="stat-label mb-2">Total Payouts Received</div>
            <div className="text-3xl font-mono font-bold text-jade-400">₹{partner?.total_payouts_received?.toLocaleString() || '—'}</div>
          </div>
        </div>

        {/* Coverage */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card-glow">
            <h3 className="section-title text-jade-400 mb-4 flex items-center gap-2"><CheckCircle className="w-4 h-4" />Coverage Inclusions</h3>
            <ul className="space-y-3">
              {INCLUSIONS.map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                  <CheckCircle className="w-4 h-4 text-jade-400 mt-0.5 flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="card-glow">
            <h3 className="section-title text-coral-400 mb-4 flex items-center gap-2"><XCircle className="w-4 h-4" />Exclusions</h3>
            <ul className="space-y-3">
              {EXCLUSIONS.map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                  <XCircle className="w-4 h-4 text-coral-400 mt-0.5 flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
