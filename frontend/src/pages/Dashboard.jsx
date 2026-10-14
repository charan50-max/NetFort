import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Play, 
  GitCompareArrows, 
  ShieldCheck, 
  ShieldAlert, 
  Activity, 
  Cpu, 
  ArrowRight, 
  RotateCcw,
  Sparkles,
  Layers,
  SearchCheck,
  CheckCircle2,
  XCircle
} from 'lucide-react';
import OutcomeBadge from '../components/common/OutcomeBadge';

export default function Dashboard() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [sumRes, histRes] = await Promise.all([
        fetch('/api/simulations/latest'),
        fetch('/api/simulations/history')
      ]);
      if (sumRes.ok) setSummary(await sumRes.json());
      if (histRes.ok) setHistory(await histRes.json());
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLaunchDefaultSimulation = async () => {
    try {
      const res = await fetch('/api/simulations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: 'enterprise_100', model_type: 'stateful' })
      });
      if (res.ok) {
        navigate('/simulation');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleLaunchComparison = async () => {
    try {
      await fetch('/api/comparisons?scenario_id=enterprise_100', { method: 'POST' });
      navigate('/compare');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Hero Banner */}
      <div className="bg-surface border border-appBorder rounded-xl p-6 md:p-8 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xs">
        <div className="max-w-2xl space-y-2">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-peach text-brown">
            <Sparkles className="w-3.5 h-3.5" />
            100 Synthetic Packets Stream
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-brown tracking-tight">
            Firewall Laboratory & Inspection Engine
          </h2>
          <p className="text-sm text-appText-muted leading-relaxed">
            Witness how <strong>stateless packet filtering</strong> and <strong>stateful inspection</strong> evaluate the same synthetic traffic stream. Observe connection tracking in action, inspect individual frame disassemblies on double-click, and analyze exact metric divergence.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 flex-shrink-0">
          <button
            onClick={handleLaunchDefaultSimulation}
            className="flex items-center justify-center gap-2 px-5 py-2.5 bg-brown hover:bg-brown-light text-white text-sm font-semibold rounded-lg shadow-sm transition-colors"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>Start Live Simulation</span>
          </button>
          <button
            onClick={handleLaunchComparison}
            className="flex items-center justify-center gap-2 px-5 py-2.5 bg-canvas hover:bg-stone/20 text-brown border border-appBorder text-sm font-semibold rounded-lg transition-colors"
          >
            <GitCompareArrows className="w-4 h-4" />
            <span>Compare Firewalls</span>
          </button>
        </div>
      </div>

      {/* 4 Summary KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Total Packets */}
        <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-appText-muted">Total Packets</span>
            <span className="p-2 bg-canvas rounded-lg text-brown border border-appBorder">
              <Layers className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-mono font-bold text-appText">
              {summary ? summary.total_packets : 100}
            </div>
            <div className="text-xs text-appText-muted mt-1">
              Synthetic stream size
            </div>
          </div>
        </div>

        {/* Card 2: Allowed */}
        <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-appText-muted">Allowed Packets</span>
            <span className="p-2 bg-allowed-soft rounded-lg text-allowed border border-allowed-border">
              <ShieldCheck className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-mono font-bold text-allowed">
              {summary ? summary.allowed_count : 0}
            </div>
            <div className="text-xs text-appText-muted mt-1">
              {summary ? `${summary.allow_rate}% acceptance rate` : 'Awaiting simulation run'}
            </div>
          </div>
        </div>

        {/* Card 3: Blocked */}
        <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-appText-muted">Blocked Packets</span>
            <span className="p-2 bg-blocked-soft rounded-lg text-blocked border border-blocked-border">
              <ShieldAlert className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-mono font-bold text-blocked">
              {summary ? summary.blocked_count : 0}
            </div>
            <div className="text-xs text-appText-muted mt-1">
              {summary ? `${summary.block_rate}% rejection rate` : 'Awaiting simulation run'}
            </div>
          </div>
        </div>

        {/* Card 4: Active Connections */}
        <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-appText-muted">Tracked Flows</span>
            <span className="p-2 bg-peach/40 rounded-lg text-brown border border-peach">
              <Cpu className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-mono font-bold text-taupe">
              {summary ? summary.active_connections : 0}
            </div>
            <div className="text-xs text-appText-muted mt-1">
              Active state table sessions
            </div>
          </div>
        </div>
      </div>

      {/* Middle Section: Recent Run & How It Works */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Run Card */}
        <div className="bg-surface border border-appBorder rounded-xl p-6 shadow-xs flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-appBorder pb-3">
              <h3 className="font-bold text-base text-brown">Latest Simulation State</h3>
              {summary && (
                <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-canvas text-appText border border-appBorder">
                  Status: {summary.status.toUpperCase()}
                </span>
              )}
            </div>

            {summary ? (
              <div className="space-y-3 text-xs">
                <div className="flex justify-between py-1.5 border-b border-appBorder/50">
                  <span className="text-appText-muted">Scenario:</span>
                  <span className="font-semibold text-appText">{summary.scenario_name}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-appBorder/50">
                  <span className="text-appText-muted">Model Evaluated:</span>
                  <span className="font-semibold capitalize text-brown">{summary.model_type} Firewall</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-appBorder/50">
                  <span className="text-appText-muted">Progress:</span>
                  <span className="font-mono font-semibold text-appText">
                    {summary.processed_packets} / {summary.total_packets} packets evaluated
                  </span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-appText-muted">Created Timestamp:</span>
                  <span className="font-mono text-appText">{new Date(summary.created_at).toLocaleTimeString()}</span>
                </div>
              </div>
            ) : (
              <p className="text-xs text-appText-muted">No simulation has been executed yet.</p>
            )}
          </div>

          <div className="pt-4 border-t border-appBorder flex items-center justify-between">
            <span className="text-xs text-appText-muted">Ready to inspect?</span>
            <Link
              to="/simulation"
              className="text-xs font-semibold text-brown hover:text-brown-light flex items-center gap-1"
            >
              Open Live Simulation <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* How It Works Visual Flow */}
        <div className="bg-surface border border-appBorder rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-appBorder pb-3">
            <h3 className="font-bold text-base text-brown">Engine Lifecycle</h3>
            <span className="text-xs text-appText-muted">4-Step Architecture</span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3.5 bg-canvas rounded-lg border border-appBorder space-y-1">
              <div className="font-bold text-brown flex items-center gap-1.5">
                <span className="w-5 h-5 rounded-full bg-peach text-brown flex items-center justify-center text-[11px] font-mono">1</span>
                Generate
              </div>
              <p className="text-[11px] text-appText-muted leading-relaxed">
                Deterministic 100-packet synthetic stream loaded into the engine queue.
              </p>
            </div>

            <div className="p-3.5 bg-canvas rounded-lg border border-appBorder space-y-1">
              <div className="font-bold text-brown flex items-center gap-1.5">
                <span className="w-5 h-5 rounded-full bg-peach text-brown flex items-center justify-center text-[11px] font-mono">2</span>
                Inspect
              </div>
              <p className="text-[11px] text-appText-muted leading-relaxed">
                Validates headers, queries conntrack state table, and scans ordered rules.
              </p>
            </div>

            <div className="p-3.5 bg-canvas rounded-lg border border-appBorder space-y-1">
              <div className="font-bold text-brown flex items-center gap-1.5">
                <span className="w-5 h-5 rounded-full bg-peach text-brown flex items-center justify-center text-[11px] font-mono">3</span>
                Decide
              </div>
              <p className="text-[11px] text-appText-muted leading-relaxed">
                Dispatches to ALLOW or BLOCK lane with concrete plain-English reasoning.
              </p>
            </div>

            <div className="p-3.5 bg-canvas rounded-lg border border-appBorder space-y-1">
              <div className="font-bold text-brown flex items-center gap-1.5">
                <span className="w-5 h-5 rounded-full bg-peach text-brown flex items-center justify-center text-[11px] font-mono">4</span>
                Measure
              </div>
              <p className="text-[11px] text-appText-muted leading-relaxed">
                Computes acceptance ratios, disagreement rate, and latency metrics.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Section: Recommended Demo Card */}
      <div className="bg-peach/25 border border-peach rounded-xl p-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="font-bold text-base text-brown">Recommended Presentation Flow</span>
            <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-peach text-brown border border-peach-dark/30">
              Curated for 1-2 min Demo
            </span>
          </div>
          <p className="text-xs text-appText-muted max-w-3xl leading-relaxed">
            Run the <strong>Enterprise Web & Multi-Service Stream</strong> through Live Simulation to explain legitimate return traffic and blocked scans. Next, launch <strong>Compare Firewalls</strong> to instantly show how stateless and stateful engines differ on return packets!
          </p>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <Link
            to="/compare"
            className="px-4 py-2 bg-brown hover:bg-brown-light text-white text-xs font-semibold rounded-md shadow-xs transition-colors flex items-center gap-1.5"
          >
            <GitCompareArrows className="w-3.5 h-3.5" />
            <span>Launch Dual Comparison</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
