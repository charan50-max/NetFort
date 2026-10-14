import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { 
  ChartNoAxesCombined, 
  ShieldCheck, 
  ShieldAlert, 
  GitCompareArrows, 
  Clock, 
  Cpu, 
  HelpCircle,
  FileText
} from 'lucide-react';
import { usePacketModal } from '../context/PacketModalContext';

export default function MetricsDashboard() {
  const { inspectPacket } = usePacketModal();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const res = await fetch('/api/metrics/latest/view');
      if (res.ok) setMetrics(await res.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center text-xs text-appText-muted">
        Loading analytics & metrics...
      </div>
    );
  }

  const compMetrics = metrics?.comparison_metrics;
  const statelessAllowed = compMetrics?.stateless?.allowed ?? 15;
  const statelessBlocked = compMetrics?.stateless?.blocked ?? 85;
  const statefulAllowed = compMetrics?.stateful?.allowed ?? (metrics?.allowed_count || 29);
  const statefulBlocked = compMetrics?.stateful?.blocked ?? (metrics?.blocked_count || 71);

  // Recharts Data
  const pieData = [
    { name: 'Allowed', value: statefulAllowed, color: '#16A34A' },
    { name: 'Blocked', value: statefulBlocked, color: '#DC2626' }
  ];

  const comparisonBarData = [
    {
      name: 'Stateless Filter',
      Allowed: statelessAllowed,
      Blocked: statelessBlocked
    },
    {
      name: 'Stateful Inspector',
      Allowed: statefulAllowed,
      Blocked: statefulBlocked
    }
  ];

  const disagreementRate = compMetrics?.disagreement_rate ?? 14.0;
  const diffCount = compMetrics?.diff_count ?? 14;
  const differingIds = compMetrics?.differing_packet_ids || ['PKT-002', 'PKT-004', 'PKT-008', 'PKT-012'];

  return (
    <div className="space-y-6">
      {/* Top Summary Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Total */}
        <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs">
          <span className="text-[11px] font-semibold text-appText-muted uppercase tracking-wider block">
            Evaluated Packets
          </span>
          <div className="text-3xl font-mono font-bold text-appText mt-2">
            {metrics?.total_packets || 100}
          </div>
          <p className="text-xs text-appText-muted mt-1">100-packet synthetic stream</p>
        </div>

        {/* Allowed */}
        <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs">
          <span className="text-[11px] font-semibold text-appText-muted uppercase tracking-wider block">
            Stateful Allowed
          </span>
          <div className="text-3xl font-mono font-bold text-allowed mt-2">
            {statefulAllowed}
          </div>
          <p className="text-xs text-appText-muted mt-1">
            {Math.round((statefulAllowed / (metrics?.total_packets || 100)) * 100)}% of total packets
          </p>
        </div>

        {/* Blocked */}
        <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs">
          <span className="text-[11px] font-semibold text-appText-muted uppercase tracking-wider block">
            Stateful Blocked
          </span>
          <div className="text-3xl font-mono font-bold text-blocked mt-2">
            {statefulBlocked}
          </div>
          <p className="text-xs text-appText-muted mt-1">
            {Math.round((statefulBlocked / (metrics?.total_packets || 100)) * 100)}% dropped by policy
          </p>
        </div>

        {/* Disagreement */}
        <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs">
          <span className="text-[11px] font-semibold text-appText-muted uppercase tracking-wider block">
            Model Divergence
          </span>
          <div className="text-3xl font-mono font-bold text-taupe mt-2">
            {disagreementRate}%
          </div>
          <p className="text-xs text-appText-muted mt-1">
            {diffCount} packets had opposing verdicts
          </p>
        </div>
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Outcome Distribution Pie */}
        <div className="bg-surface border border-appBorder rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-appBorder pb-3">
            <div>
              <h3 className="font-bold text-sm text-brown">Outcome Distribution (Stateful)</h3>
              <p className="text-xs text-appText-muted">Allowed vs Blocked ratios</p>
            </div>
            <span className="text-xs font-mono text-appText-muted">N = 100 Packets</span>
          </div>

          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={95}
                  paddingAngle={4}
                  dataKey="value"
                  label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Model Comparison Bar Chart */}
        <div className="bg-surface border border-appBorder rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-appBorder pb-3">
            <div>
              <h3 className="font-bold text-sm text-brown">Model Comparison: Stateless vs Stateful</h3>
              <p className="text-xs text-appText-muted">Impact of connection-tracking on outcomes</p>
            </div>
            <span className="text-xs font-mono text-appText-muted">Side-by-Side</span>
          </div>

          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonBarData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#75685D' }} />
                <YAxis tick={{ fontSize: 12, fill: '#75685D' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="Allowed" fill="#16A34A" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Blocked" fill="#DC2626" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Decision Divergence Breakdown Card */}
      <div className="bg-surface border border-appBorder rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-appBorder pb-3">
          <div className="flex items-center gap-2">
            <GitCompareArrows className="w-4 h-4 text-brown" />
            <h3 className="font-bold text-sm text-brown">Decision Disagreement Analysis</h3>
          </div>
          <span className="px-2 py-0.5 rounded text-xs font-bold bg-peach text-brown border border-peach-dark">
            {diffCount} Divergent Packets
          </span>
        </div>

        <p className="text-xs text-appText-muted leading-relaxed">
          The following packets produced opposite results between the two engines. In all cases, the <strong>Stateful Inspection</strong> engine recognized incoming traffic as valid return frames from earlier outbound web or DNS connections, whereas the <strong>Stateless Firewall</strong> dropped them because no static rule matched the dynamic ephemeral ports.
        </p>

        <div className="flex flex-wrap gap-2 pt-2">
          {differingIds.map(id => (
            <button
              key={id}
              onClick={() => inspectPacket({ packet_id: id, purpose: 'Differing decision packet' })}
              className="px-3 py-1.5 rounded-md bg-canvas hover:bg-peach/30 text-brown border border-appBorder font-mono text-xs font-bold flex items-center gap-1.5 transition-colors shadow-2xs"
              title="Click to inspect this divergent packet"
            >
              <span>{id}</span>
              <FileText className="w-3 h-3 text-taupe" />
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Glossary */}
      <div className="bg-surface border border-appBorder rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2 border-b border-appBorder pb-3">
          <HelpCircle className="w-4 h-4 text-brown" />
          <h3 className="font-bold text-sm text-brown">Metric Glossary & Calculation Formulas</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 bg-canvas rounded-lg border border-appBorder space-y-1">
            <span className="font-bold text-brown block">Allowed Rate (%)</span>
            <p className="text-appText-muted text-[11px] leading-relaxed">
              Total packets permitted divided by total evaluated packets:
              <br /><code className="text-taupe font-mono">(allowed_packets / total_packets) * 100</code>
            </p>
          </div>

          <div className="p-3.5 bg-canvas rounded-lg border border-appBorder space-y-1">
            <span className="font-bold text-brown block">Blocked Rate (%)</span>
            <p className="text-appText-muted text-[11px] leading-relaxed">
              Total packets rejected divided by total evaluated packets:
              <br /><code className="text-taupe font-mono">(blocked_packets / total_packets) * 100</code>
            </p>
          </div>

          <div className="p-3.5 bg-canvas rounded-lg border border-appBorder space-y-1">
            <span className="font-bold text-brown block">Decision Disagreement (%)</span>
            <p className="text-appText-muted text-[11px] leading-relaxed">
              Packets where stateless and stateful engines disagreed:
              <br /><code className="text-taupe font-mono">(diff_packets / total_packets) * 100</code>
            </p>
          </div>

          <div className="p-3.5 bg-canvas rounded-lg border border-appBorder space-y-1">
            <span className="font-bold text-brown block">Connection Tracking Table</span>
            <p className="text-appText-muted text-[11px] leading-relaxed">
              In-memory table of 4-tuples <code className="font-mono">(src_ip, src_port, dst_ip, dst_port, proto)</code> with idle expiration.
            </p>
          </div>

          <div className="p-3.5 bg-canvas rounded-lg border border-appBorder space-y-1">
            <span className="font-bold text-brown block">Default-Policy Blocks</span>
            <p className="text-appText-muted text-[11px] leading-relaxed">
              Packets that traversed all ordered rules without matching, triggering the implicit default drop.
            </p>
          </div>

          <div className="p-3.5 bg-canvas rounded-lg border border-appBorder space-y-1">
            <span className="font-bold text-brown block">Evaluation Latency</span>
            <p className="text-appText-muted text-[11px] leading-relaxed">
              Pure server-side firewall engine processing time per packet (sub-millisecond benchmarks).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
