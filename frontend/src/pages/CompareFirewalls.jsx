import React, { useState, useEffect } from 'react';
import { 
  GitCompareArrows, 
  RotateCcw, 
  Play, 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  Filter, 
  Download, 
  HelpCircle,
  Activity,
  ArrowRight
} from 'lucide-react';
import OutcomeBadge from '../components/common/OutcomeBadge';
import { usePacketModal } from '../context/PacketModalContext';

export default function CompareFirewalls() {
  const { inspectPacket } = usePacketModal();

  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState('enterprise_100');
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filterDiffOnly, setFilterDiffOnly] = useState(false);
  const [speedMode, setSpeedMode] = useState('instant'); // instant, fast, normal

  useEffect(() => {
    fetchScenarios();
    loadLatestComparison();
  }, []);

  const fetchScenarios = async () => {
    try {
      const res = await fetch('/api/scenarios');
      if (res.ok) setScenarios(await res.json());
    } catch (err) {
      console.error(err);
    }
  };

  const loadLatestComparison = async () => {
    try {
      const res = await fetch('/api/comparisons/latest');
      if (res.ok) {
        setComparisonData(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const runComparison = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/comparisons?scenario_id=${selectedScenario}`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setComparisonData(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const results = comparisonData ? comparisonData.results : [];
  const displayRows = filterDiffOnly ? results.filter(r => r.is_difference) : results;

  return (
    <div className="space-y-6">
      {/* Top Controls Bar */}
      <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <div>
              <label className="text-[11px] font-semibold text-appText-muted block mb-1">Scenario (100 Packets)</label>
              <select
                value={selectedScenario}
                onChange={(e) => setSelectedScenario(e.target.value)}
                className="text-xs font-medium bg-canvas border border-appBorder rounded-md px-3 py-1.5 text-appText focus:outline-none focus:ring-1 focus:ring-brown"
              >
                {scenarios.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.packet_count} Pkts)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[11px] font-semibold text-appText-muted block mb-1">Execution Speed</label>
              <div className="flex items-center gap-1 bg-canvas border border-appBorder rounded-md p-0.5 text-xs">
                {['instant', 'fast'].map(m => (
                  <button
                    key={m}
                    onClick={() => setSpeedMode(m)}
                    className={`px-3 py-1 rounded text-[11px] font-medium capitalize transition-colors ${
                      speedMode === m ? 'bg-peach text-brown font-bold' : 'text-appText-muted hover:text-appText'
                    }`}
                  >
                    {m === 'instant' ? 'Instant Evaluation' : 'Animated Demo'}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={runComparison}
              disabled={loading}
              className="flex items-center gap-1.5 px-4 py-2 bg-brown hover:bg-brown-light text-white text-xs font-semibold rounded-md shadow-xs transition-colors disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{loading ? 'Evaluating 100 Packets...' : 'Run 100-Packet Comparison'}</span>
            </button>
            {comparisonData && (
              <a
                href={`/api/export/${comparisonData.comparison_id}/csv`}
                download
                className="flex items-center gap-1.5 px-3 py-2 bg-canvas hover:bg-stone/20 text-brown border border-appBorder text-xs font-medium rounded-md transition-colors"
                title="Download CSV"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export CSV</span>
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Two Parallel Firewall Columns */}
      {comparisonData && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Left Column: Stateless Packet Filtering */}
          <div className="bg-surface border border-stone rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-appBorder">
              <div>
                <span className="text-[10px] font-bold text-appText-muted uppercase tracking-wider block">
                  Model A
                </span>
                <h3 className="font-bold text-base text-brown">Packet-Filtering Firewall</h3>
                <span className="text-xs text-appText-muted">Stateless (No Session Memory)</span>
              </div>
              <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-canvas border border-appBorder text-taupe">
                STATELESS
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-canvas border border-appBorder rounded-lg">
                <span className="text-appText-muted text-[11px]">Allowed Packets:</span>
                <div className="text-2xl font-mono font-bold text-allowed mt-1">
                  {comparisonData.stateless_allowed}
                </div>
              </div>
              <div className="p-3 bg-canvas border border-appBorder rounded-lg">
                <span className="text-appText-muted text-[11px]">Blocked Packets:</span>
                <div className="text-2xl font-mono font-bold text-blocked mt-1">
                  {comparisonData.stateless_blocked}
                </div>
              </div>
            </div>

            <p className="text-xs text-appText-muted leading-relaxed">
              Evaluates every packet strictly against ordered static rules. Reply packets to outbound web requests are dropped unless explicit incoming rules exist for high client ports.
            </p>
          </div>

          {/* Right Column: Stateful Inspection */}
          <div className="bg-surface border border-stone rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-appBorder">
              <div>
                <span className="text-[10px] font-bold text-appText-muted uppercase tracking-wider block">
                  Model B
                </span>
                <h3 className="font-bold text-base text-brown">Stateful-Inspection Firewall</h3>
                <span className="text-xs text-appText-muted">Dynamic Connection Tracking</span>
              </div>
              <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-peach text-brown font-bold border border-peach-dark">
                STATE-TRACKING
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-canvas border border-appBorder rounded-lg">
                <span className="text-appText-muted text-[11px]">Allowed Packets:</span>
                <div className="text-2xl font-mono font-bold text-allowed mt-1">
                  {comparisonData.stateful_allowed}
                </div>
              </div>
              <div className="p-3 bg-canvas border border-appBorder rounded-lg">
                <span className="text-appText-muted text-[11px]">Blocked Packets:</span>
                <div className="text-2xl font-mono font-bold text-blocked mt-1">
                  {comparisonData.stateful_blocked}
                </div>
              </div>
            </div>

            <p className="text-xs text-appText-muted leading-relaxed">
              Maintains an active bidirectional state table. When a permitted outbound connection occurs, incoming replies are automatically recognized as <code className="text-brown font-bold">ESTABLISHED</code> and permitted.
            </p>
          </div>
        </div>
      )}

      {/* Difference Strip */}
      {comparisonData && (
        <div className="bg-peach/30 border border-peach rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-peach rounded-lg text-brown">
              <GitCompareArrows className="w-5 h-5" />
            </div>
            <div>
              <div className="font-bold text-sm text-brown">
                Decision Divergence: {comparisonData.diff_count} Differences ({comparisonData.disagreement_rate}% Disagreement)
              </div>
              <div className="text-xs text-appText-muted">
                {comparisonData.same_count} of 100 packets had identical decisions; {comparisonData.diff_count} packets differed due to connection-tracking state.
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setFilterDiffOnly(!filterDiffOnly)}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                filterDiffOnly
                  ? 'bg-brown text-white shadow-xs'
                  : 'bg-canvas text-brown hover:bg-stone/20 border border-appBorder'
              }`}
            >
              <Filter className="w-3.5 h-3.5" />
              <span>{filterDiffOnly ? 'Show All 100 Packets' : 'Show Differences Only'}</span>
            </button>
          </div>
        </div>
      )}

      {/* 100-Packet Side-by-Side Comparison Table */}
      <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs space-y-3">
        <div className="flex items-center justify-between pb-3 border-b border-appBorder">
          <div>
            <h3 className="font-bold text-sm text-brown">
              Side-by-Side Decision Matrix ({displayRows.length} Packets Displayed)
            </h3>
            <p className="text-xs text-appText-muted">
              Double-click any packet row to inspect its original raw wire format
            </p>
          </div>
          <span className="text-xs font-mono text-appText-muted">
            100 Synthetic Packets Stream
          </span>
        </div>

        <div className="overflow-x-auto max-h-[500px]">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead className="bg-canvas border-b border-appBorder text-appText-muted uppercase tracking-wider text-[11px] sticky top-0 font-sans">
              <tr>
                <th className="py-2.5 px-3">#</th>
                <th className="py-2.5 px-3">Packet ID</th>
                <th className="py-2.5 px-3">Source → Dest</th>
                <th className="py-2.5 px-3">Proto</th>
                <th className="py-2.5 px-3">Stateless</th>
                <th className="py-2.5 px-3">Stateful</th>
                <th className="py-2.5 px-3">Verdict</th>
                <th className="py-2.5 px-3 font-sans">Explanation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-appBorder">
              {displayRows.map((row) => (
                <tr
                  key={row.packet_id}
                  onDoubleClick={() => inspectPacket(row)}
                  className={`cursor-pointer transition-colors ${
                    row.is_difference ? 'bg-peach/25 hover:bg-peach/40' : 'hover:bg-canvas'
                  }`}
                  title="Double click to inspect original packet wire dump"
                >
                  <td className="py-2.5 px-3 text-appText-muted">{row.sequence}</td>
                  <td className="py-2.5 px-3 font-bold text-brown">{row.packet_id}</td>
                  <td className="py-2.5 px-3 text-appText">
                    {row.source_ip}:{row.source_port} → {row.destination_ip}:{row.port}
                  </td>
                  <td className="py-2.5 px-3 text-taupe">{row.protocol}</td>
                  <td className="py-2.5 px-3">
                    <OutcomeBadge action={row.stateless_action} size="sm" />
                  </td>
                  <td className="py-2.5 px-3">
                    <OutcomeBadge action={row.stateful_action} size="sm" />
                  </td>
                  <td className="py-2.5 px-3">
                    {row.is_difference ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-peach text-brown border border-peach-dark">
                        DIFFERENCE
                      </span>
                    ) : (
                      <span className="text-[10px] text-appText-muted font-sans">Same</span>
                    )}
                  </td>
                  <td className="py-2.5 px-3 font-sans text-appText text-xs truncate max-w-sm">
                    {row.difference_explanation || row.stateful_reason}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
