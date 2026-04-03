import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-navy-800 border border-navy-600 rounded-xl px-4 py-3 text-xs space-y-1">
      <div className="text-slate-400 mb-2">{label}</div>
      {payload.map(p => (
        <div key={p.dataKey} className="flex justify-between gap-4">
          <span style={{ color: p.color }}>{p.name}</span>
          <span className="font-mono font-semibold text-slate-200">₹{p.value?.toLocaleString()}</span>
        </div>
      ))}
      {payload[0] && payload[1] && (
        <div className="flex justify-between gap-4 pt-1 border-t border-navy-600 mt-1">
          <span className="text-slate-500">EDI</span>
          <span className="font-mono font-semibold text-amber-400">
            ₹{Math.max(0, payload[1].value - payload[0].value).toLocaleString()}
          </span>
        </div>
      )}
    </div>
  );
};

export default function EarningsTrendChart({ data = [], loading }) {
  if (loading) return (
    <div className="h-64 bg-navy-800 rounded-xl animate-pulse" />
  );

  const chartData = data.map(d => ({
    label: `D${d.day}`,
    'Actual Earnings': d.actual_earnings,
    'Expected Earnings': d.expected_earnings,
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <defs>
          <linearGradient id="gradActual" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#2dd4bf" stopOpacity={0.25} />
            <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0.02} />
          </linearGradient>
          <linearGradient id="gradExpected" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor="#94a3b8" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#94a3b8" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(255,255,255,0.04)" />
        <XAxis dataKey="label" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} interval={4} />
        <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => `₹${v}`} width={55} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
        <Area type="monotone" dataKey="Expected Earnings" stroke="#475569" fill="url(#gradExpected)" strokeWidth={1.5} strokeDasharray="4 3" dot={false} />
        <Area type="monotone" dataKey="Actual Earnings"   stroke="#2dd4bf" fill="url(#gradActual)"   strokeWidth={2.5} dot={false} activeDot={{ r: 4, fill: '#2dd4bf' }} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
