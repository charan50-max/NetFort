import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  GitCompareArrows,
  Play,
  ShieldCheck,
  ShieldAlert,
  Filter,
  Download,
  Activity,
  Zap,
  Square,
} from 'lucide-react';
import OutcomeBadge from '../components/common/OutcomeBadge';
import { usePacketModal } from '../context/PacketModalContext';

// ─── tiny CSS injected once ────────────────────────────────────────────────
const ANIM_STYLE = `
@keyframes rowSlideIn {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.pkt-row-enter {
  animation: rowSlideIn 0.18s ease-out forwards;
}
`;

function injectAnimStyle() {
  if (document.getElementById('__netfort-compare-anim')) return;
  const el = document.createElement('style');
  el.id = '__netfort-compare-anim';
  el.textContent = ANIM_STYLE;
  document.head.appendChild(el);
}

// ─── component ─────────────────────────────────────────────────────────────
export default function CompareFirewalls() {
  const { inspectPacket } = usePacketModal();
  injectAnimStyle();

  const [scenarios, setScenarios]               = useState([]);
  const [selectedScenario, setSelectedScenario] = useState('enterprise_100');
  const [comparisonData, setComparisonData]     = useState(null);
  const [loading, setLoading]                   = useState(false);
  const [filterDiffOnly, setFilterDiffOnly]     = useState(false);
  const [speedMode, setSpeedMode]               = useState('fast'); // instant | fast

  // Animation state
  const [animating, setAnimating]               = useState(false);
  const [animProgress, setAnimProgress]         = useState(0);   // 0-100
  const [displayedRows, setDisplayedRows]       = useState([]);  // rows revealed so far
  const [liveStats, setLiveStats]               = useState(null);// incremental stats

  const allResultsRef = useRef([]);      // full backend result array
  const intervalRef   = useRef(null);    // setInterval handle
  const rowCountRef   = useRef(0);       // how many rows pushed so far

  useEffect(() => {
    fetchScenarios();
    loadLatestComparison();
    return () => clearInterval(intervalRef.current);
  }, []);

  // ── data fetching ───────────────────────────────────────────────────────
  const fetchScenarios = async () => {
    try {
      const res = await fetch('/api/scenarios');
      if (res.ok) setScenarios(await res.json());
    } catch (err) { console.error(err); }
  };

  const loadLatestComparison = async () => {
    try {
      const res = await fetch('/api/comparisons/latest');
      if (res.ok) {
        const data = await res.json();
        setComparisonData(data);
        setDisplayedRows(data.results);
        setLiveStats(buildStats(data.results));
      }
    } catch (err) { console.error(err); }
  };

  // ── stats helper ────────────────────────────────────────────────────────
  const buildStats = (rows) => {
    const sl_a = rows.filter(r => r.stateless_action === 'ALLOW').length;
    const st_a = rows.filter(r => r.stateful_action  === 'ALLOW').length;
    const diff  = rows.filter(r => r.is_difference).length;
    return {
      stateless_allowed: sl_a,
      stateless_blocked: rows.length - sl_a,
      stateful_allowed:  st_a,
      stateful_blocked:  rows.length - st_a,
      diff_count:        diff,
      same_count:        rows.length - diff,
    };
  };

  // ── start animation after data arrives ─────────────────────────────────
  const startAnimation = useCallback((data) => {
    clearInterval(intervalRef.current);
    allResultsRef.current = data.results;
    rowCountRef.current   = 0;
    setDisplayedRows([]);
    setLiveStats({ stateless_allowed: 0, stateless_blocked: 0,
                   stateful_allowed: 0, stateful_blocked: 0,
                   diff_count: 0, same_count: 0 });
    setAnimProgress(0);
    setAnimating(true);

    const total     = data.results.length;
    const TICK_MS   = speedMode === 'fast' ? 35 : 100;
    const BATCH     = speedMode === 'fast' ? 2 : 1;   // rows per tick

    intervalRef.current = setInterval(() => {
      const idx = rowCountRef.current;
      if (idx >= total) {
        clearInterval(intervalRef.current);
        setAnimating(false);
        setComparisonData(data);           // lock in final stats from server
        setLiveStats(buildStats(data.results));
        return;
      }

      const nextIdx = Math.min(idx + BATCH, total);
      rowCountRef.current = nextIdx;

      setDisplayedRows(prev => {
        const slice = allResultsRef.current.slice(idx, nextIdx);
        return [...prev, ...slice];
      });
      setAnimProgress(Math.round((nextIdx / total) * 100));
      setLiveStats(buildStats(allResultsRef.current.slice(0, nextIdx)));
    }, TICK_MS);
  }, [speedMode]);

  const stopAnimation = () => {
    clearInterval(intervalRef.current);
    const data = { ...comparisonData };   // comparisonData may be stale — use allResults
    const all  = allResultsRef.current;
    setDisplayedRows(all);
    setAnimProgress(100);
    setAnimating(false);
    setLiveStats(buildStats(all));
  };

  // ── run comparison ──────────────────────────────────────────────────────
  const runComparison = async () => {
    setLoading(true);
    clearInterval(intervalRef.current);
    try {
      const res = await fetch(`/api/comparisons?scenario_id=${selectedScenario}`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        if (speedMode === 'instant') {
          setComparisonData(data);
          setDisplayedRows(data.results);
          setLiveStats(buildStats(data.results));
          setAnimProgress(100);
        } else {
          // Keep comparisonData for header info but animate rows
          setComparisonData(data);
          startAnimation(data);
        }
      }
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  // ── derived display ─────────────────────────────────────────────────────
  const statsToShow = liveStats || (comparisonData
    ? buildStats(comparisonData.results ?? [])
    : null);

  const rowsToDisplay = filterDiffOnly
    ? displayedRows.filter(r => r.is_difference)
    : displayedRows;

  const total = comparisonData?.results?.length ?? 100;

  // ── render ──────────────────────────────────────────────────────────────
  return (
    <div className="space-y-6">

      {/* ── Top Controls ── */}
      <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            {/* Scenario picker */}
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

            {/* Speed mode toggle */}
            <div>
              <label className="text-[11px] font-semibold text-appText-muted block mb-1">Execution Speed</label>
              <div className="flex items-center gap-1 bg-canvas border border-appBorder rounded-md p-0.5 text-xs">
                {[
                  { key: 'instant', label: 'Instant Evaluation', Icon: Zap },
                  { key: 'fast',    label: 'Animated Demo',      Icon: Activity },
                ].map(({ key, label, Icon }) => (
                  <button
                    key={key}
                    onClick={() => setSpeedMode(key)}
                    disabled={animating}
                    className={`px-3 py-1 rounded text-[11px] font-medium flex items-center gap-1 transition-colors disabled:opacity-40 ${
                      speedMode === key ? 'bg-peach text-brown font-bold' : 'text-appText-muted hover:text-appText'
                    }`}
                  >
                    <Icon className="w-3 h-3" />
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            {animating ? (
              <button
                onClick={stopAnimation}
                className="flex items-center gap-1.5 px-4 py-2 bg-blocked/80 hover:bg-blocked text-white text-xs font-semibold rounded-md shadow-xs transition-colors"
              >
                <Square className="w-3.5 h-3.5 fill-current" />
                <span>Skip to End</span>
              </button>
            ) : (
              <button
                onClick={runComparison}
                disabled={loading}
                className="flex items-center gap-1.5 px-4 py-2 bg-brown hover:bg-brown-light text-white text-xs font-semibold rounded-md shadow-xs transition-colors disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{loading ? 'Fetching Packets…' : 'Run 100-Packet Comparison'}</span>
              </button>
            )}
            {comparisonData && !animating && (
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

        {/* Progress bar (shown while animating) */}
        {animating && (
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] text-appText-muted font-mono">
              <span className="flex items-center gap-1.5">
                <span className="inline-block w-2 h-2 rounded-full bg-brown animate-pulse" />
                Processing packet {displayedRows.length} of {total}…
              </span>
              <span>{animProgress}%</span>
            </div>
            <div className="h-1.5 w-full rounded-full bg-canvas overflow-hidden border border-appBorder">
              <div
                className="h-full rounded-full bg-brown transition-all duration-75 ease-linear"
                style={{ width: `${animProgress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* ── Two Parallel Firewall Columns ── */}
      {(comparisonData || animating) && statsToShow && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {[
            {
              label: 'Model A', tag: 'STATELESS', tagCls: 'bg-canvas border border-appBorder text-taupe',
              title: 'Packet-Filtering Firewall', sub: 'Stateless (No Session Memory)',
              allowed: statsToShow.stateless_allowed, blocked: statsToShow.stateless_blocked,
              desc: 'Evaluates every packet strictly against ordered static rules. Reply packets to outbound web requests are dropped unless explicit incoming rules exist for high client ports.',
              Icon: ShieldAlert,
            },
            {
              label: 'Model B', tag: 'STATE-TRACKING', tagCls: 'bg-peach text-brown font-bold border border-peach-dark',
              title: 'Stateful-Inspection Firewall', sub: 'Dynamic Connection Tracking',
              allowed: statsToShow.stateful_allowed, blocked: statsToShow.stateful_blocked,
              desc: <>Maintains an active bidirectional state table. When a permitted outbound connection occurs, incoming replies are automatically recognized as <code className="text-brown font-bold">ESTABLISHED</code> and permitted.</>,
              Icon: ShieldCheck,
            },
          ].map(({ label, tag, tagCls, title, sub, allowed, blocked, desc, Icon }) => (
            <div key={label} className="bg-surface border border-stone rounded-xl p-5 shadow-xs space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-appBorder">
                <div>
                  <span className="text-[10px] font-bold text-appText-muted uppercase tracking-wider block">{label}</span>
                  <h3 className="font-bold text-base text-brown">{title}</h3>
                  <span className="text-xs text-appText-muted">{sub}</span>
                </div>
                <span className={`px-2 py-0.5 rounded text-[11px] font-mono ${tagCls}`}>{tag}</span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 bg-canvas border border-appBorder rounded-lg">
                  <span className="text-appText-muted text-[11px]">Allowed Packets:</span>
                  <div className="text-2xl font-mono font-bold text-allowed mt-1 tabular-nums transition-all duration-150">
                    {allowed}
                  </div>
                </div>
                <div className="p-3 bg-canvas border border-appBorder rounded-lg">
                  <span className="text-appText-muted text-[11px]">Blocked Packets:</span>
                  <div className="text-2xl font-mono font-bold text-blocked mt-1 tabular-nums transition-all duration-150">
                    {blocked}
                  </div>
                </div>
              </div>

              <p className="text-xs text-appText-muted leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      )}

      {/* ── Difference Strip ── */}
      {(comparisonData || animating) && statsToShow && (
        <div className="bg-peach/30 border border-peach rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-peach rounded-lg text-brown">
              <GitCompareArrows className="w-5 h-5" />
            </div>
            <div>
              <div className="font-bold text-sm text-brown">
                Decision Divergence:{' '}
                <span className="tabular-nums">{statsToShow.diff_count}</span> Differences
                {comparisonData && !animating && ` (${comparisonData.disagreement_rate}% Disagreement)`}
              </div>
              <div className="text-xs text-appText-muted">
                <span className="tabular-nums">{statsToShow.same_count}</span> of{' '}
                <span className="tabular-nums">{displayedRows.length}</span> packets evaluated —{' '}
                {animating ? (
                  <span className="text-brown font-medium animate-pulse">analysing…</span>
                ) : (
                  <span>{statsToShow.diff_count} differed due to connection-tracking state</span>
                )}
              </div>
            </div>
          </div>

          {!animating && (
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
          )}
        </div>
      )}

      {/* ── Side-by-Side Table ── */}
      <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs space-y-3">
        <div className="flex items-center justify-between pb-3 border-b border-appBorder">
          <div>
            <h3 className="font-bold text-sm text-brown">
              Side-by-Side Decision Matrix ({rowsToDisplay.length} Packets Displayed)
            </h3>
            <p className="text-xs text-appText-muted">
              Double-click any packet row to inspect its original raw wire format
            </p>
          </div>
          <span className="text-xs font-mono text-appText-muted">100 Synthetic Packets Stream</span>
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
              {rowsToDisplay.length === 0 && !animating && !loading && (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-appText-muted font-sans text-sm">
                    Click <strong className="text-brown">Run 100-Packet Comparison</strong> to begin.
                  </td>
                </tr>
              )}
              {rowsToDisplay.length === 0 && (animating || loading) && (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-appText-muted font-sans text-sm">
                    <span className="inline-block w-2 h-2 rounded-full bg-brown animate-ping mr-2" />
                    Initialising…
                  </td>
                </tr>
              )}
              {rowsToDisplay.map((row, idx) => (
                <tr
                  key={row.packet_id}
                  onDoubleClick={() => inspectPacket(row)}
                  // Only animate the last few rows so we don't re-animate everything on re-render
                  className={`cursor-pointer transition-colors ${
                    row.is_difference ? 'bg-peach/25 hover:bg-peach/40' : 'hover:bg-canvas'
                  } ${animating && idx >= displayedRows.length - 2 ? 'pkt-row-enter' : ''}`}
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
