import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  FastForward, 
  ChevronRight, 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Terminal, 
  Layers,
  Activity,
  ArrowRight
} from 'lucide-react';
import OutcomeBadge from '../components/common/OutcomeBadge';
import { usePacketModal } from '../context/PacketModalContext';

export default function LiveSimulation() {
  const { inspectPacket } = usePacketModal();

  // Configuration state
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState('enterprise_100');
  const [modelType, setModelType] = useState('stateful');
  const [speedMs, setSpeedMs] = useState(2000); // 2.0s presentation default

  // Simulation run state
  const [runId, setRunId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, running, paused, completed, stopped
  const [queue, setQueue] = useState([]);
  const [allowedLanes, setAllowedLanes] = useState([]);
  const [blockedLanes, setBlockedLanes] = useState([]);
  const [currentPacket, setCurrentPacket] = useState(null);
  const [evalStep, setEvalStep] = useState(0); // 0=validate, 1=conntrack, 2=rules, 3=decided
  const [latestExplanation, setLatestExplanation] = useState(null);
  const [logRecords, setLogRecords] = useState([]);
  const [filterOutcome, setFilterOutcome] = useState('ALL');
  const [selectedRecord, setSelectedRecord] = useState(null);

  // Counters
  const [processedCount, setProcessedCount] = useState(0);
  const [allowedCount, setAllowedCount] = useState(0);
  const [blockedCount, setBlockedCount] = useState(0);
  const [activeConnections, setActiveConnections] = useState(0);

  const timerRef = useRef(null);

  useEffect(() => {
    fetchScenarios();
    return () => clearInterval(timerRef.current);
  }, []);

  const fetchScenarios = async () => {
    try {
      const res = await fetch('/api/scenarios');
      if (res.ok) {
        const data = await res.json();
        setScenarios(data);
        if (data.length > 0) setSelectedScenario(data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const initSimulation = async () => {
    try {
      const res = await fetch('/api/simulations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: selectedScenario, model_type: modelType })
      });
      if (res.ok) {
        const data = await res.json();
        setRunId(data.run_id);
        setStatus('ready');
        setProcessedCount(0);
        setAllowedCount(0);
        setBlockedCount(0);
        setActiveConnections(0);
        setAllowedLanes([]);
        setBlockedLanes([]);
        setCurrentPacket(null);
        setLatestExplanation(null);
        setLogRecords([]);
        setSelectedRecord(null);

        // Fetch raw scenario queue packets
        const qRes = await fetch(`/api/scenarios/${selectedScenario}/packets`);
        if (qRes.ok) {
          const pkts = await qRes.json();
          setQueue(pkts);
        }
        return data.run_id;
      }
    } catch (err) {
      console.error('Failed to init simulation:', err);
    }
    return null;
  };

  // Step single packet
  const stepOnePacket = async (activeRunId) => {
    const idToUse = activeRunId || runId;
    if (!idToUse) return false;

    try {
      setEvalStep(0);
      const res = await fetch(`/api/simulations/${idToUse}/step?batch_size=1`, { method: 'POST' });
      if (!res.ok) return false;

      const data = await res.json();
      const stepRes = data.step_result;
      const summary = data.summary;

      if (stepRes) {
        const pkt = stepRes.packet;
        setCurrentPacket(pkt);
        setLatestExplanation(stepRes);

        // Animate engine steps
        setTimeout(() => setEvalStep(1), speedMs * 0.2);
        setTimeout(() => setEvalStep(2), speedMs * 0.4);
        setTimeout(() => {
          setEvalStep(3);
          // Push to completed lanes
          if (stepRes.action === 'ALLOW') {
            setAllowedLanes(prev => [stepRes, ...prev.slice(0, 19)]);
          } else {
            setBlockedLanes(prev => [stepRes, ...prev.slice(0, 19)]);
          }

          // Update queue and logs
          setQueue(prev => prev.filter(p => p.packet_id !== pkt.packet_id));
          setLogRecords(prev => [stepRes, ...prev]);
          setProcessedCount(summary.processed_packets);
          setAllowedCount(summary.allowed_count);
          setBlockedCount(summary.blocked_count);
          setActiveConnections(summary.active_connections);
        }, speedMs * 0.7);
      }

      if (data.finished) {
        setStatus('completed');
        clearInterval(timerRef.current);
        return false;
      }
      return true;
    } catch (err) {
      console.error('Step error:', err);
      return false;
    }
  };

  const handleStart = async () => {
    let currentId = runId;
    if (!currentId || status === 'completed' || status === 'stopped') {
      currentId = await initSimulation();
    }
    if (!currentId) return;

    setStatus('running');
    clearInterval(timerRef.current);

    // Initial immediate step
    await stepOnePacket(currentId);

    // Continuous ticker
    timerRef.current = setInterval(async () => {
      const continueStepping = await stepOnePacket(currentId);
      if (!continueStepping) {
        clearInterval(timerRef.current);
      }
    }, speedMs);
  };

  const handlePause = () => {
    clearInterval(timerRef.current);
    setStatus('paused');
    if (runId) fetch(`/api/simulations/${runId}/pause`, { method: 'POST' });
  };

  const handleResume = () => {
    setStatus('running');
    clearInterval(timerRef.current);
    if (runId) fetch(`/api/simulations/${runId}/resume`, { method: 'POST' });

    timerRef.current = setInterval(async () => {
      const continueStepping = await stepOnePacket(runId);
      if (!continueStepping) {
        clearInterval(timerRef.current);
      }
    }, speedMs);
  };

  const handleStop = () => {
    clearInterval(timerRef.current);
    setStatus('stopped');
    if (runId) fetch(`/api/simulations/${runId}/stop`, { method: 'POST' });
  };

  const handleRestart = async () => {
    clearInterval(timerRef.current);
    await initSimulation();
  };

  const handleManualStep = async () => {
    let currentId = runId;
    if (!currentId || status === 'completed' || status === 'stopped') {
      currentId = await initSimulation();
    }
    if (!currentId) return;
    setStatus('paused');
    clearInterval(timerRef.current);
    await stepOnePacket(currentId);
  };

  const filteredLogs = logRecords.filter(r => {
    if (filterOutcome === 'ALL') return true;
    return r.action === filterOutcome;
  });

  return (
    <div className="space-y-6">
      {/* Page Header & Controls Bar */}
      <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            {/* Scenario Selector */}
            <div>
              <label className="text-[11px] font-semibold text-appText-muted block mb-1">Traffic Scenario</label>
              <select
                value={selectedScenario}
                disabled={status === 'running'}
                onChange={(e) => { setSelectedScenario(e.target.value); handleRestart(); }}
                className="text-xs font-medium bg-canvas border border-appBorder rounded-md px-3 py-1.5 text-appText focus:outline-none focus:ring-1 focus:ring-brown disabled:opacity-50"
              >
                {scenarios.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.packet_count} Pkts)
                  </option>
                ))}
              </select>
            </div>

            {/* Model Selector */}
            <div>
              <label className="text-[11px] font-semibold text-appText-muted block mb-1">Firewall Architecture</label>
              <select
                value={modelType}
                disabled={status === 'running'}
                onChange={(e) => { setModelType(e.target.value); handleRestart(); }}
                className="text-xs font-medium bg-canvas border border-appBorder rounded-md px-3 py-1.5 text-appText focus:outline-none focus:ring-1 focus:ring-brown disabled:opacity-50"
              >
                <option value="stateful">Stateful Inspection (Conntrack Table)</option>
                <option value="stateless">Stateless Packet Filtering (Static Rules)</option>
              </select>
            </div>

            {/* Speed Selector */}
            <div>
              <label className="text-[11px] font-semibold text-appText-muted block mb-1">Pacing Speed</label>
              <div className="flex items-center gap-1 bg-canvas border border-appBorder rounded-md p-0.5 text-xs">
                {[
                  { label: '2.0s', val: 2000 },
                  { label: '1.0s', val: 1000 },
                  { label: '0.5s', val: 500 },
                  { label: '0.1s', val: 100 }
                ].map(s => (
                  <button
                    key={s.val}
                    onClick={() => setSpeedMs(s.val)}
                    className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                      speedMs === s.val ? 'bg-peach text-brown font-bold' : 'text-appText-muted hover:text-appText'
                    }`}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 pt-2 lg:pt-0">
            {status !== 'running' ? (
              <button
                onClick={status === 'paused' ? handleResume : handleStart}
                className="flex items-center gap-1.5 px-4 py-2 bg-brown hover:bg-brown-light text-white text-xs font-semibold rounded-md shadow-xs transition-colors"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{status === 'paused' ? 'Resume' : 'Start Simulation'}</span>
              </button>
            ) : (
              <button
                onClick={handlePause}
                className="flex items-center gap-1.5 px-4 py-2 bg-taupe hover:bg-taupe-dark text-white text-xs font-semibold rounded-md shadow-xs transition-colors"
              >
                <Pause className="w-3.5 h-3.5" />
                <span>Pause</span>
              </button>
            )}

            <button
              onClick={handleManualStep}
              disabled={status === 'running' || status === 'completed'}
              className="flex items-center gap-1.5 px-3 py-2 bg-canvas hover:bg-stone/20 text-brown border border-appBorder text-xs font-medium rounded-md transition-colors disabled:opacity-40"
              title="Advance exactly one packet"
            >
              <ChevronRight className="w-4 h-4" />
              <span>Step Next</span>
            </button>

            <button
              onClick={handleStop}
              disabled={status !== 'running' && status !== 'paused'}
              className="p-2 bg-canvas hover:bg-stone/20 text-appText-muted hover:text-blocked border border-appBorder rounded-md transition-colors disabled:opacity-40"
              title="Stop simulation"
            >
              <Square className="w-4 h-4" />
            </button>

            <button
              onClick={handleRestart}
              className="p-2 bg-canvas hover:bg-stone/20 text-appText-muted hover:text-brown border border-appBorder rounded-md transition-colors"
              title="Restart simulation"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Progress Bar & Status Line */}
        <div className="space-y-1.5 pt-2 border-t border-appBorder">
          <div className="flex justify-between text-xs text-appText-muted">
            <span className="font-medium text-appText">
              Progress: <span className="font-mono font-bold text-brown">{processedCount}</span> of 100 packets evaluated
            </span>
            <span className="font-mono">{Math.round((processedCount / 100) * 100)}%</span>
          </div>
          <div className="w-full h-2 bg-canvas rounded-full overflow-hidden border border-appBorder">
            <div 
              className="h-full bg-peach-dark transition-all duration-300"
              style={{ width: `${(processedCount / 100) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Main 3-Stage Traffic Flow Canvas */}
      <div className="bg-surface border border-appBorder rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-appBorder">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-brown" />
            <h3 className="font-bold text-base text-brown">Traffic Flow & Inspection Canvas</h3>
          </div>
          <span className="text-xs text-appText-muted">
            Tip: Double-click any packet tile to view its raw wire data
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch min-h-[380px]">
          {/* Stage 1: Traffic Source Queue (4 cols) */}
          <div className="lg:col-span-4 bg-canvas border border-appBorder rounded-xl p-4 flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-appBorder flex-shrink-0">
              <span className="text-xs font-bold text-brown uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-taupe" />
                Packet Queue ({queue.length})
              </span>
              <span className="text-[11px] text-appText-muted font-mono">100 Packets</span>
            </div>

            <div className="flex-1 overflow-y-auto space-y-2 pt-3 max-h-[350px] pr-1">
              {queue.length === 0 ? (
                <div className="text-center py-12 text-xs text-appText-muted">
                  Queue empty. All packets evaluated.
                </div>
              ) : (
                queue.slice(0, 12).map((pkt, idx) => (
                  <div
                    key={pkt.packet_id}
                    onDoubleClick={() => inspectPacket(pkt)}
                    className="p-2.5 bg-surface hover:bg-peach/20 border border-appBorder rounded-lg cursor-pointer transition-all hover:scale-[1.01] shadow-2xs space-y-1"
                    title="Double click to inspect raw packet"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-mono font-bold text-brown">{pkt.packet_id}</span>
                      <span className="px-1.5 py-0.2 text-[10px] font-mono bg-stone/20 rounded text-appText-muted">
                        {pkt.protocol}
                      </span>
                    </div>
                    <div className="text-[11px] font-mono text-appText flex items-center justify-between">
                      <span className="truncate max-w-[110px]">{pkt.source_ip}:{pkt.source_port || 0}</span>
                      <ArrowRight className="w-3 h-3 text-taupe flex-shrink-0 mx-1" />
                      <span className="truncate max-w-[110px]">{pkt.destination_ip}:{pkt.port}</span>
                    </div>
                    <div className="text-[10px] text-appText-muted truncate">
                      {pkt.purpose}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Stage 2: Firewall Engine Panel (4 cols) */}
          <div className="lg:col-span-4 bg-canvas border border-peach/80 rounded-xl p-5 flex flex-col justify-between shadow-xs">
            <div>
              <div className="flex items-center justify-between border-b border-appBorder pb-3">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-brown text-peach">
                    <Terminal className="w-4 h-4" />
                  </span>
                  <div>
                    <div className="font-bold text-sm text-brown capitalize">{modelType} Firewall</div>
                    <div className="text-[10px] text-appText-muted">Inspection Engine</div>
                  </div>
                </div>
                <span className={`px-2 py-0.5 text-xs font-mono font-bold rounded ${
                  status === 'running' ? 'bg-peach text-brown animate-pulse' : 'bg-stone/30 text-appText-muted'
                }`}>
                  {status.toUpperCase()}
                </span>
              </div>

              {/* Current Packet In Flight */}
              <div className="my-4 p-3.5 bg-surface border border-stone/50 rounded-lg shadow-2xs">
                <span className="text-[10px] font-bold text-appText-muted uppercase tracking-wider block mb-1">
                  Packet Under Inspection
                </span>
                {currentPacket ? (
                  <div 
                    onDoubleClick={() => inspectPacket(currentPacket)}
                    className="cursor-pointer space-y-1"
                    title="Double click to inspect raw packet"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-sm text-brown">{currentPacket.packet_id}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-peach text-brown">
                        {currentPacket.protocol}
                      </span>
                    </div>
                    <div className="font-mono text-xs text-appText">
                      {currentPacket.source_ip}:{currentPacket.source_port} → {currentPacket.destination_ip}:{currentPacket.port}
                    </div>
                    <div className="text-xs text-appText-muted line-clamp-1">
                      {currentPacket.purpose}
                    </div>
                  </div>
                ) : (
                  <div className="py-4 text-center text-xs text-appText-muted">
                    Engine idle. Click Start to begin.
                  </div>
                )}
              </div>

              {/* Step Checklist */}
              <div className="space-y-2 text-xs">
                <span className="text-[10px] font-bold text-appText-muted uppercase tracking-wider block">
                  Evaluation Steps
                </span>
                {[
                  { step: 0, text: 'Validate headers & ports' },
                  { step: 1, text: modelType === 'stateful' ? 'Check connection state table' : 'Stateless: skip session state' },
                  { step: 2, text: 'Evaluate ordered firewall rules' },
                  { step: 3, text: 'Apply decision & update counters' }
                ].map(s => {
                  const isCurrent = (evalStep === s.step && status === 'running');
                  const isPassed = (evalStep > s.step || status === 'completed');
                  return (
                    <div 
                      key={s.step} 
                      className={`flex items-center gap-2 p-2 rounded border transition-colors ${
                        isCurrent 
                          ? 'bg-peach text-brown font-bold border-peach-dark' 
                          : isPassed 
                            ? 'bg-surface text-appText border-appBorder' 
                            : 'bg-canvas text-appText-muted border-transparent opacity-60'
                      }`}
                    >
                      {isPassed ? (
                        <CheckCircle2 className="w-4 h-4 text-brown flex-shrink-0" />
                      ) : (
                        <span className="w-4 h-4 rounded-full border border-stone flex items-center justify-center text-[10px] font-mono">
                          {s.step + 1}
                        </span>
                      )}
                      <span className="text-xs">{s.text}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="pt-3 border-t border-appBorder flex items-center justify-between text-[11px] text-appText-muted">
              <span>Tracked Connections:</span>
              <span className="font-mono font-bold text-brown">{activeConnections} active</span>
            </div>
          </div>

          {/* Stage 3: Decision Lanes (4 cols) */}
          <div className="lg:col-span-4 flex flex-col gap-4">
            {/* Allowed Lane */}
            <div className="flex-1 bg-allowed-soft/30 border border-allowed-border rounded-xl p-3 flex flex-col">
              <div className="flex items-center justify-between pb-2 border-b border-allowed-border/60">
                <span className="text-xs font-bold text-allowed flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4" />
                  ALLOWED LANE ({allowedCount})
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-allowed-soft text-allowed border border-allowed-border">
                  PASS
                </span>
              </div>
              <div className="flex-1 overflow-y-auto space-y-1.5 pt-2 max-h-[140px] pr-1">
                {allowedLanes.length === 0 ? (
                  <div className="text-center py-6 text-xs text-appText-muted">No allowed packets yet</div>
                ) : (
                  allowedLanes.slice(0, 5).map((rec, i) => (
                    <div
                      key={i}
                      onDoubleClick={() => inspectPacket(rec)}
                      className="p-2 bg-surface hover:bg-allowed-soft/40 border border-allowed-border rounded-md text-xs cursor-pointer shadow-2xs transition-transform hover:scale-[1.01]"
                      title="Double click to inspect raw packet"
                    >
                      <div className="flex justify-between font-mono">
                        <span className="font-bold text-allowed">{rec.packet_id}</span>
                        <span className="text-appText-muted">{rec.packet.destination_ip}:{rec.packet.port}</span>
                      </div>
                      <div className="text-[10px] text-appText-muted truncate mt-0.5">
                        {rec.matched_rule_name || rec.reason}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Blocked Lane */}
            <div className="flex-1 bg-blocked-soft/30 border border-blocked-border rounded-xl p-3 flex flex-col">
              <div className="flex items-center justify-between pb-2 border-b border-blocked-border/60">
                <span className="text-xs font-bold text-blocked flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4" />
                  BLOCKED LANE ({blockedCount})
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blocked-soft text-blocked border border-blocked-border">
                  DROP
                </span>
              </div>
              <div className="flex-1 overflow-y-auto space-y-1.5 pt-2 max-h-[140px] pr-1">
                {blockedLanes.length === 0 ? (
                  <div className="text-center py-6 text-xs text-appText-muted">No blocked packets yet</div>
                ) : (
                  blockedLanes.slice(0, 5).map((rec, i) => (
                    <div
                      key={i}
                      onDoubleClick={() => inspectPacket(rec)}
                      className="p-2 bg-surface hover:bg-blocked-soft/40 border border-blocked-border rounded-md text-xs cursor-pointer shadow-2xs transition-transform hover:scale-[1.01]"
                      title="Double click to inspect raw packet"
                    >
                      <div className="flex justify-between font-mono">
                        <span className="font-bold text-blocked">{rec.packet_id}</span>
                        <span className="text-appText-muted">{rec.packet.destination_ip}:{rec.packet.port}</span>
                      </div>
                      <div className="text-[10px] text-appText-muted truncate mt-0.5">
                        {rec.matched_rule_name || rec.reason}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Real-Time Decision Explanation Panel */}
        {latestExplanation && (
          <div className="p-4 bg-canvas border border-stone rounded-xl space-y-2 mt-4 animate-in fade-in">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-appBorder pb-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-brown">Decision Explanation:</span>
                <OutcomeBadge action={latestExplanation.action} size="sm" />
                <span className="font-mono text-xs text-appText-muted">
                  ({latestExplanation.packet_id})
                </span>
              </div>
              <div className="text-xs text-appText-muted flex items-center gap-3">
                {latestExplanation.matched_rule_name && (
                  <span>Matched: <strong className="text-brown">{latestExplanation.matched_rule_name}</strong></span>
                )}
                {latestExplanation.connection_state && (
                  <span>State: <strong className="font-mono text-taupe">{latestExplanation.connection_state}</strong></span>
                )}
                <span className="font-mono text-stone">{latestExplanation.processing_time_ms} ms</span>
              </div>
            </div>
            <p className="text-xs text-appText leading-relaxed">
              <strong>Why? </strong> {latestExplanation.reason}
            </p>
          </div>
        )}
      </div>

      {/* Live Event Log Table with Filters */}
      <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-appBorder">
          <div>
            <h3 className="font-bold text-sm text-brown">Real-Time Packet Event Log</h3>
            <p className="text-xs text-appText-muted">Click row for details; double-click for raw frame dump</p>
          </div>

          <div className="flex items-center gap-1.5 bg-canvas p-1 rounded-md border border-appBorder text-xs">
            {['ALL', 'ALLOW', 'BLOCK'].map(f => (
              <button
                key={f}
                onClick={() => setFilterOutcome(f)}
                className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
                  filterOutcome === f ? 'bg-peach text-brown' : 'text-appText-muted hover:text-appText'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto max-h-[350px]">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-canvas border-b border-appBorder text-appText-muted uppercase tracking-wider text-[11px] sticky top-0">
              <tr>
                <th className="py-2.5 px-3">#</th>
                <th className="py-2.5 px-3">Packet ID</th>
                <th className="py-2.5 px-3">Source → Dest</th>
                <th className="py-2.5 px-3">Protocol</th>
                <th className="py-2.5 px-3">Outcome</th>
                <th className="py-2.5 px-3">Matched Rule / Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-appBorder font-mono">
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-appText-muted font-sans">
                    No packet events recorded yet.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => (
                  <tr
                    key={log.packet_id}
                    onClick={() => setSelectedRecord(log)}
                    onDoubleClick={() => inspectPacket(log)}
                    className="hover:bg-peach/15 cursor-pointer transition-colors"
                  >
                    <td className="py-2.5 px-3 text-appText-muted">{log.sequence}</td>
                    <td className="py-2.5 px-3 font-bold text-brown">{log.packet_id}</td>
                    <td className="py-2.5 px-3 text-appText">
                      {log.packet.source_ip}:{log.packet.source_port} → {log.packet.destination_ip}:{log.packet.port}
                    </td>
                    <td className="py-2.5 px-3 text-taupe">{log.packet.protocol}</td>
                    <td className="py-2.5 px-3">
                      <OutcomeBadge action={log.action} size="sm" />
                    </td>
                    <td className="py-2.5 px-3 font-sans text-appText text-xs truncate max-w-md">
                      {log.matched_rule_name || log.reason}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
