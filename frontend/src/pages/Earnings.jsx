import { useState, useEffect, useCallback } from 'react';
import Topbar from '../components/layout/Topbar';
import EarningsTrendChart from '../components/charts/EarningsTrendChart';
import { fetchEarningsTrend, isUsingMockData } from '../utils/api';
import { useApp } from '../store/AppContext';

export default function Earnings() {
  const { stressMode, setUsingMock } = useApp();
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const r = await fetchEarningsTrend('GG-2024-04821', 30, stressMode);
    setTrend(r.trend || []);
    setUsingMock(isUsingMockData());
    setLoading(false);
  }, [stressMode, setUsingMock]);

  useEffect(() => { load(); }, [load]);

  const totalActual = trend.reduce((s, d) => s + d.actual_earnings, 0);
  const totalExpected = trend.reduce((s, d) => s + d.expected_earnings, 0);
  const totalEDI = trend.reduce((s, d) => s + d.edi, 0);

  return (
    <div className="animate-fade-in">
      <Topbar title="Earnings Analysis" subtitle="30-day income vs expectation" onRefresh={load} loading={loading} />
      <div className="p-8 space-y-6">
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Total Actual Earnings', value: `₹${Math.round(totalActual).toLocaleString()}`, color: 'text-teal-400' },
            { label: 'Total Expected Earnings', value: `₹${Math.round(totalExpected).toLocaleString()}`, color: 'text-slate-300' },
            { label: 'Total EDI (Deficit)', value: `₹${Math.round(totalEDI).toLocaleString()}`, color: 'text-amber-400' },
          ].map(s => (
            <div key={s.label} className="card-glow">
              <div className="stat-label mb-2">{s.label}</div>
              <div className={`text-3xl font-mono font-bold ${s.color}`}>{s.value}</div>
            </div>
          ))}
        </div>
        <div className="card-glow">
          <h3 className="section-title mb-5">Daily Earnings vs Expectation</h3>
          <EarningsTrendChart data={trend} loading={loading} />
        </div>
        <div className="card-glow overflow-auto">
          <h3 className="section-title mb-4">Daily Breakdown</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-navy-700">
                {['Day', 'Actual (₹)', 'Expected (₹)', 'EDI (₹)', 'Loss %'].map(h => (
                  <th key={h} className="pb-3 pr-4 stat-label">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {trend.slice(0, 14).map(d => {
                const lossPct = Math.round((d.edi / d.expected_earnings) * 100);
                return (
                  <tr key={d.day} className="border-b border-navy-800 hover:bg-navy-800/40 transition-colors">
                    <td className="py-2.5 pr-4 text-slate-400 font-mono">D{d.day}</td>
                    <td className="py-2.5 pr-4 text-teal-400 font-mono">₹{Math.round(d.actual_earnings).toLocaleString()}</td>
                    <td className="py-2.5 pr-4 text-slate-300 font-mono">₹{Math.round(d.expected_earnings).toLocaleString()}</td>
                    <td className="py-2.5 pr-4 text-amber-400 font-mono">₹{Math.round(d.edi).toLocaleString()}</td>
                    <td className="py-2.5">
                      <span className={`badge ${lossPct > 35 ? 'badge-coral' : lossPct > 20 ? 'badge-amber' : 'badge-jade'}`}>
                        {lossPct}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
