import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-navy-800 border border-navy-600 rounded-xl px-4 py-3 text-xs">
      <div className="text-slate-300 font-semibold">{payload[0]?.payload?.factor}</div>
      <div className="text-teal-400 font-mono mt-1">{(payload[0]?.value * 100).toFixed(1)}%</div>
    </div>
  );
};

export default function CausationRadar({ data }) {
  const radarData = data ? [
    { factor: 'Environment', value: data.environment || 0 },
    { factor: 'Peer Trend',  value: data.peer_trend || 0 },
    { factor: 'Demand Drop', value: data.demand || 0 },
    { factor: 'Individ. Dev', value: data.individual_deviation || 0 },
  ] : [];

  return (
    <div className="card-glow">
      <h3 className="section-title mb-4">Causation Breakdown</h3>
      <ResponsiveContainer width="100%" height={220}>
        <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
          <PolarGrid stroke="rgba(255,255,255,0.06)" />
          <PolarAngleAxis dataKey="factor" tick={{ fill: '#94a3b8', fontSize: 10, fontFamily: 'Plus Jakarta Sans' }} />
          <Radar
            name="Causation"
            dataKey="value"
            stroke="#2dd4bf"
            fill="#2dd4bf"
            fillOpacity={0.15}
            strokeWidth={2}
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
