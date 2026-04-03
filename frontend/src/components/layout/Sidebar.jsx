import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Shield, BarChart3, MapPin,
  Settings, AlertTriangle, Zap, Users, FileText, ChevronRight
} from 'lucide-react';
import { useApp } from '../../store/AppContext';
import clsx from 'clsx';

const NAV = [
  { section: 'Partner', items: [
    { to: '/',          icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/policy',    icon: Shield,          label: 'My Policy' },
    { to: '/earnings',  icon: BarChart3,       label: 'Earnings' },
    { to: '/payouts',   icon: Zap,             label: 'Payouts' },
  ]},
  { section: 'Admin', items: [
    { to: '/admin',     icon: Users,           label: 'Admin Panel' },
    { to: '/risk-pool', icon: FileText,        label: 'Risk Pool' },
    { to: '/heatmap',   icon: MapPin,          label: 'City Heatmap' },
  ]},
];

const EXTERNAL_NAV = [
  { href: '/demo.html',       icon: '🎬', label: 'Demo Engine' },
  { href: '/fraud.html',      icon: '🔍', label: 'Fraud Detection' },
  { href: '/dashboard.html',  icon: '🛵', label: 'Rider Dashboard' },
  { href: '/simulation.html', icon: '⚡', label: 'Live Scenario' },
  { href: '/history.html',    icon: '📋', label: 'History & ROI' },
  { href: '/home.html',       icon: '🏠', label: 'GigGuard Home' },
];

export default function Sidebar() {
  const { stressMode, toggleStress, usingMock } = useApp();
  const loc = useLocation();

  return (
    <aside className="w-64 flex-shrink-0 flex flex-col bg-navy-900 border-r border-navy-700 h-screen sticky top-0 overflow-y-auto">
      {/* Logo */}
      <div className="px-5 pt-6 pb-5 border-b border-navy-700">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center flex-shrink-0 glow-teal">
            <Shield className="w-5 h-5 text-navy-950" />
          </div>
          <div>
            <div className="font-display text-lg leading-none text-slate-100">ARIA<span className="text-teal-400">-Gig</span></div>
            <div className="text-[10px] text-slate-500 font-medium tracking-widest uppercase mt-0.5">GigGuard™</div>
          </div>
        </div>
        {usingMock && (
          <div className="mt-3 px-2.5 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/25 flex items-center gap-2">
            <AlertTriangle className="w-3 h-3 text-amber-400 flex-shrink-0" />
            <span className="text-[10px] text-amber-400 font-medium">Demo data mode</span>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-6">
        {NAV.map(group => (
          <div key={group.section}>
            <div className="px-3 mb-2 text-[10px] uppercase tracking-widest text-slate-600 font-semibold">{group.section}</div>
            <div className="space-y-0.5">
              {group.items.map(({ to, icon: Icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) => clsx('sidebar-link', isActive && 'active')}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span className="flex-1">{label}</span>
                  {loc.pathname === to && <ChevronRight className="w-3 h-3 opacity-50" />}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
        {/* GigGuard HTML pages */}
        <div>
          <div className="px-3 mb-2 text-[10px] uppercase tracking-widest text-slate-600 font-semibold">GigGuard App</div>
          <div className="space-y-0.5">
            {EXTERNAL_NAV.map(({ href, icon, label }) => (
              <a key={href} href={href} className="sidebar-link">
                <span className="text-sm flex-shrink-0">{icon}</span>
                <span className="flex-1 text-xs">{label}</span>
              </a>
            ))}
          </div>
        </div>
      </nav>

      {/* Stress mode toggle */}
      <div className="px-4 pb-5 pt-3 border-t border-navy-700">
        <button
          onClick={toggleStress}
          className={clsx(
            'w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-300 border',
            stressMode
              ? 'bg-coral-500/15 border-coral-500/40 text-coral-400'
              : 'bg-navy-800 border-navy-600 text-slate-400 hover:text-slate-200 hover:border-navy-500'
          )}
        >
          <AlertTriangle className={clsx('w-4 h-4', stressMode && 'animate-pulse')} />
          <span className="flex-1 text-left text-xs leading-tight">
            {stressMode ? '⚠ High Economic Stress' : 'Economic Stress Mode'}
          </span>
          <div className={clsx(
            'w-9 h-5 rounded-full transition-all duration-300 relative flex-shrink-0',
            stressMode ? 'bg-coral-500' : 'bg-navy-600'
          )}>
            <div className={clsx(
              'absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all duration-300',
              stressMode ? 'left-[18px]' : 'left-0.5'
            )} />
          </div>
        </button>
        {stressMode && (
          <p className="mt-2 text-[10px] text-coral-400/70 px-1 leading-relaxed">
            Simulating Iran–Israel fuel spike, demand collapse, and AQI surge
          </p>
        )}
      </div>
    </aside>
  );
}
