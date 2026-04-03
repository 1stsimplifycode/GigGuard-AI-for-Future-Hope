import clsx from 'clsx';

export default function WorkabilityGauge({ score = 0, size = 'lg' }) {
  const pct = Math.max(0, Math.min(100, score));
  const angle = -135 + (pct / 100) * 270; // -135° to +135°
  const r = size === 'lg' ? 60 : 42;
  const cx = size === 'lg' ? 80 : 56;
  const cy = size === 'lg' ? 80 : 56;
  const svgSize = size === 'lg' ? 160 : 112;
  const strokeW = size === 'lg' ? 10 : 8;
  const circumference = 2 * Math.PI * r;
  const dashLen = circumference * (270 / 360);
  const progress = dashLen * (pct / 100);

  const color = pct >= 70 ? '#2dd4bf' : pct >= 50 ? '#fbbf24' : '#f43f5e';
  const label = pct >= 70 ? 'Workable' : pct >= 50 ? 'Caution' : 'At Risk';
  const bgArcId = `bg-${Math.random().toString(36).slice(2)}`;

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <svg
          width={svgSize}
          height={svgSize * 0.75}
          viewBox={`0 0 ${svgSize} ${svgSize * 0.75}`}
          className="overflow-visible"
        >
          <defs>
            <linearGradient id={bgArcId} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={color} stopOpacity="0.2" />
              <stop offset="100%" stopColor={color} stopOpacity="0.8" />
            </linearGradient>
          </defs>
          {/* Background arc */}
          <circle
            cx={cx} cy={cy} r={r}
            fill="none"
            stroke="rgba(255,255,255,0.05)"
            strokeWidth={strokeW}
            strokeDasharray={`${dashLen} ${circumference}`}
            strokeDashoffset={-circumference * (45 / 360)}
            strokeLinecap="round"
            transform={`rotate(-225 ${cx} ${cy})`}
          />
          {/* Progress arc */}
          <circle
            cx={cx} cy={cy} r={r}
            fill="none"
            stroke={color}
            strokeWidth={strokeW}
            strokeDasharray={`${progress} ${circumference}`}
            strokeDashoffset={-circumference * (45 / 360)}
            strokeLinecap="round"
            transform={`rotate(-225 ${cx} ${cy})`}
            style={{ filter: `drop-shadow(0 0 6px ${color}80)`, transition: 'all 1s ease' }}
          />
          {/* Needle */}
          <g transform={`rotate(${angle}, ${cx}, ${cy})`}>
            <line
              x1={cx} y1={cy}
              x2={cx} y2={cy - r + strokeW}
              stroke={color}
              strokeWidth="2"
              strokeLinecap="round"
            />
            <circle cx={cx} cy={cy} r={4} fill={color} />
          </g>
          {/* Score text */}
          <text
            x={cx} y={cy + (size === 'lg' ? 18 : 12)}
            textAnchor="middle"
            fill="white"
            fontSize={size === 'lg' ? 28 : 20}
            fontWeight="700"
            fontFamily="JetBrains Mono, monospace"
          >
            {Math.round(pct)}
          </text>
          <text
            x={cx} y={cy + (size === 'lg' ? 34 : 26)}
            textAnchor="middle"
            fill={color}
            fontSize={size === 'lg' ? 9 : 8}
            fontWeight="600"
            letterSpacing="2"
            textTransform="uppercase"
          >
            {label.toUpperCase()}
          </text>
        </svg>
      </div>
      <div className="mt-2 flex items-center gap-3 text-xs">
        {[
          { color: '#f43f5e', label: '<50 Payout' },
          { color: '#fbbf24', label: '50–70 Watch' },
          { color: '#2dd4bf', label: '>70 Clear' },
        ].map(item => (
          <div key={item.label} className="flex items-center gap-1.5 text-slate-500">
            <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
            {item.label}
          </div>
        ))}
      </div>
    </div>
  );
}
