import { Bell, RefreshCw, AlertTriangle } from 'lucide-react';
import { useApp } from '../../store/AppContext';
import clsx from 'clsx';

export default function Topbar({ title, subtitle, onRefresh, loading }) {
  const { stressMode, usingMock } = useApp();

  return (
    <header className="h-16 flex items-center px-8 border-b border-navy-700 bg-navy-900/60 backdrop-blur-sm sticky top-0 z-20 gap-4">
      <div className="flex-1 min-w-0">
        <h1 className="text-base font-semibold text-slate-100 truncate">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500 truncate">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {usingMock && (
          <div className="data-banner">
            <AlertTriangle className="w-3.5 h-3.5" />
            Live data unavailable – showing generated data
          </div>
        )}
        {stressMode && (
          <div className="badge badge-coral">
            <span className="w-1.5 h-1.5 rounded-full bg-coral-400 animate-pulse" />
            Economic Stress Active
          </div>
        )}
        {onRefresh && (
          <button onClick={onRefresh} className="btn-secondary !px-3 !py-2">
            <RefreshCw className={clsx('w-4 h-4', loading && 'animate-spin')} />
          </button>
        )}
        <button className="btn-secondary !px-3 !py-2 relative">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-coral-400 rounded-full" />
        </button>
        <div className="w-8 h-8 rounded-full bg-teal-500/20 border border-teal-500/30 flex items-center justify-center text-teal-400 text-xs font-bold">
          RK
        </div>
      </div>
    </header>
  );
}
