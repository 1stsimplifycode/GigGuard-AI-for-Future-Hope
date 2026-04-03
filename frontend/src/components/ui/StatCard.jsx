import clsx from 'clsx';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function StatCard({ label, value, unit, sub, trend, icon: Icon, accent = 'teal', loading }) {
  const colors = {
    teal:  { border: 'border-teal-500/20',  text: 'text-teal-400',  bg: 'bg-teal-500/10' },
    amber: { border: 'border-amber-500/20', text: 'text-amber-400', bg: 'bg-amber-500/10' },
    coral: { border: 'border-coral-500/20', text: 'text-coral-400', bg: 'bg-coral-500/10' },
    jade:  { border: 'border-jade-500/20',  text: 'text-jade-400',  bg: 'bg-jade-500/10' },
    slate: { border: 'border-slate-600/30', text: 'text-slate-400', bg: 'bg-slate-700/20' },
  };
  const c = colors[accent] || colors.teal;

  return (
    <div className={clsx('card-glow border', c.border, 'animate-slide-up')}>
      <div className="flex items-start justify-between mb-3">
        <span className="stat-label">{label}</span>
        {Icon && (
          <div className={clsx('w-8 h-8 rounded-lg flex items-center justify-center', c.bg)}>
            <Icon className={clsx('w-4 h-4', c.text)} />
          </div>
        )}
      </div>
      {loading ? (
        <div className="h-8 w-24 bg-navy-700 rounded animate-pulse mb-1" />
      ) : (
        <div className="flex items-end gap-1.5">
          <span className={clsx('stat-value', c.text)}>{value}</span>
          {unit && <span className="text-slate-500 text-sm mb-1">{unit}</span>}
        </div>
      )}
      {sub && (
        <div className="mt-2 flex items-center gap-1.5">
          {trend === 'up'   && <TrendingUp   className="w-3 h-3 text-jade-400"  />}
          {trend === 'down' && <TrendingDown  className="w-3 h-3 text-coral-400" />}
          {trend === 'flat' && <Minus         className="w-3 h-3 text-slate-500" />}
          <span className="text-xs text-slate-500">{sub}</span>
        </div>
      )}
    </div>
  );
}
