import clsx from 'clsx';

const TIER_CONFIG = {
  1: { label: 'T1', sub: '20–35% loss', rate: '50%', color: 'border-amber-500/30 bg-amber-500/10 text-amber-400' },
  2: { label: 'T2', sub: '35–55% loss', rate: '65%', color: 'border-amber-400/40 bg-amber-400/12 text-amber-300' },
  3: { label: 'T3', sub: '55–75% loss', rate: '75%', color: 'border-coral-500/30 bg-coral-500/10 text-coral-400' },
  4: { label: 'T4', sub: '75–100% loss', rate: '85%', color: 'border-coral-400/40 bg-coral-400/12 text-coral-300' },
};

export default function PayoutTierBadge({ tier, amount, active }) {
  const cfg = TIER_CONFIG[tier];
  if (!cfg) return null;
  return (
    <div className={clsx(
      'border rounded-xl p-4 transition-all duration-300',
      cfg.color,
      active ? 'scale-105 ring-2 ring-offset-2 ring-offset-navy-900 ring-amber-500/50' : 'opacity-60'
    )}>
      <div className="font-display text-2xl">{cfg.label}</div>
      <div className="text-xs mt-1 opacity-80">{cfg.sub}</div>
      <div className="text-xl font-bold font-mono mt-2">{cfg.rate}</div>
      <div className="text-xs opacity-70 mt-0.5">payout rate</div>
      {active && amount != null && (
        <div className="mt-3 pt-3 border-t border-current/20">
          <div className="text-xs opacity-70">Est. payout</div>
          <div className="font-mono font-bold">₹{amount.toLocaleString()}</div>
        </div>
      )}
    </div>
  );
}
