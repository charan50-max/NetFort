import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  Shield, 
  LayoutDashboard, 
  Activity, 
  GitCompareArrows, 
  ListFilter, 
  ChartNoAxesCombined, 
  ScrollText, 
  RotateCcw,
  Menu,
  X,
  AlertCircle
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Live Simulation', path: '/simulation', icon: Activity },
  { name: 'Compare Firewalls', path: '/compare', icon: GitCompareArrows },
  { name: 'Rules', path: '/rules', icon: ListFilter },
  { name: 'Metrics', path: '/metrics', icon: ChartNoAxesCombined },
  { name: 'Packet Log', path: '/packet-log', icon: ScrollText },
];

export default function AppShell({ children, onResetDemo }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const location = useLocation();

  const handleConfirmReset = async () => {
    setShowResetConfirm(false);
    if (onResetDemo) {
      await onResetDemo();
    } else {
      try {
        await fetch('/api/rules/reset', { method: 'POST' });
        window.location.reload();
      } catch (err) {
        console.error('Reset error:', err);
      }
    }
  };

  const getPageInfo = () => {
    switch (location.pathname) {
      case '/':
        return { title: 'Firewall Lab', subtitle: 'Explore how packet filtering and stateful inspection handle the same traffic.' };
      case '/simulation':
        return { title: 'Live Simulation', subtitle: 'Step through the 100-packet stream at a deliberate pace to observe decisions.' };
      case '/compare':
        return { title: 'Compare Firewalls', subtitle: 'Side-by-side execution of stateless packet filtering vs stateful inspection on 100 packets.' };
      case '/rules':
        return { title: 'Firewall Rules', subtitle: 'Rules are evaluated from top to bottom. The first matching rule decides the result.' };
      case '/metrics':
        return { title: 'Metrics & Analytics', subtitle: 'Clear evaluation metrics, disagreement analysis, and connection tracking statistics.' };
      case '/packet-log':
        return { title: 'Packet Log', subtitle: 'Inspect, filter, and export the entire 100-packet stream and its firewall decisions.' };
      default:
        return { title: 'NetFort Simulator', subtitle: 'Synthetic packet firewall testbed.' };
    }
  };

  const { title, subtitle } = getPageInfo();

  return (
    <div className="flex h-screen overflow-hidden bg-canvas text-appText">
      {/* Sidebar - Desktop */}
      <aside className="hidden md:flex flex-col w-60 bg-surface border-r border-appBorder flex-shrink-0 select-none">
        {/* Brand Block */}
        <div className="h-16 px-6 border-b border-appBorder flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-brown text-white flex items-center justify-center shadow-sm">
            <Shield className="w-5 h-5 text-peach" />
          </div>
          <div>
            <div className="font-bold text-base tracking-tight text-brown leading-tight">NetFort</div>
            <div className="text-[11px] text-appText-muted font-medium">Firewall Simulator v2.0</div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-peach text-brown font-semibold shadow-xs'
                      : 'text-appText-muted hover:bg-canvas hover:text-appText'
                  }`
                }
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Footer Demo Badge */}
        <div className="p-4 border-t border-appBorder bg-canvas/60">
          <div className="p-3 bg-surface rounded-lg border border-appBorder text-xs text-appText-muted space-y-1">
            <div className="flex items-center gap-1.5 font-semibold text-brown">
              <span className="w-2 h-2 rounded-full bg-allowed animate-pulse"></span>
              Demo Mode Active
            </div>
            <p className="text-[11px] leading-relaxed">
              Operating on 100 synthetic packets. Safe educational sandbox.
            </p>
          </div>
        </div>
      </aside>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 md:hidden flex">
          <div className="fixed inset-0 bg-black/40" onClick={() => setMobileMenuOpen(false)}></div>
          <div className="relative w-64 bg-surface border-r border-appBorder flex flex-col h-full z-50">
            <div className="h-16 px-6 border-b border-appBorder flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-brown text-white flex items-center justify-center">
                  <Shield className="w-4 h-4 text-peach" />
                </div>
                <span className="font-bold text-brown">NetFort</span>
              </div>
              <button onClick={() => setMobileMenuOpen(false)} className="p-1 text-appText-muted">
                <X className="w-5 h-5" />
              </button>
            </div>
            <nav className="flex-1 p-3 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium ${
                        isActive ? 'bg-peach text-brown font-semibold' : 'text-appText-muted'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-surface border-b border-appBorder px-6 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="p-1.5 rounded-md hover:bg-canvas md:hidden text-appText-muted"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-base font-bold text-brown">{title}</h1>
              <p className="text-xs text-appText-muted hidden sm:block">{subtitle}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="hidden lg:inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-semibold bg-stone/20 text-taupe border border-stone/40">
              SIMULATION ONLY
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-peach/40 text-brown border border-peach">
              100 Packets Stream
            </span>
            <button
              onClick={() => setShowResetConfirm(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-appText-muted hover:text-brown bg-canvas hover:bg-stone/20 border border-appBorder rounded-md transition-colors"
              title="Reset Demo rules and clear statistics"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Demo</span>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>

      {/* Reset Confirmation Dialog */}
      {showResetConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
          <div className="bg-surface border border-stone w-full max-w-md rounded-xl p-6 shadow-xl space-y-4">
            <div className="flex items-center gap-3 text-brown">
              <div className="p-2 rounded-full bg-peach/50">
                <AlertCircle className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-lg">Reset Demo State?</h3>
            </div>
            <p className="text-xs text-appText-muted leading-relaxed">
              This will restore the baseline educational demo rules, flush connection tracking tables, and reset statistics back to packet 1.
            </p>
            <div className="flex items-center justify-end gap-2.5 pt-2">
              <button
                onClick={() => setShowResetConfirm(false)}
                className="px-3.5 py-1.5 text-xs font-medium text-appText-muted hover:text-appText bg-canvas border border-appBorder rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmReset}
                className="px-4 py-1.5 text-xs font-semibold text-white bg-brown hover:bg-brown-light rounded-md shadow-xs"
              >
                Reset Demo
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
