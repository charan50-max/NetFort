import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Download, 
  ScrollText, 
  ChevronLeft, 
  ChevronRight, 
  Terminal, 
  X,
  FileText,
  Activity,
  ArrowRight
} from 'lucide-react';
import OutcomeBadge from '../components/common/OutcomeBadge';
import { usePacketModal } from '../context/PacketModalContext';

export default function PacketLog() {
  const { inspectPacket } = usePacketModal();

  const [packets, setPackets] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [search, setSearch] = useState('');
  const [filterOutcome, setFilterOutcome] = useState('ALL');
  const [filterProto, setFilterProto] = useState('ALL');
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [runId, setRunId] = useState(null);

  useEffect(() => {
    fetchLatestRunAndPackets();
  }, [page, pageSize, filterOutcome, search]);

  const fetchLatestRunAndPackets = async () => {
    setLoading(true);
    try {
      // First get or ensure a simulation run
      let currentRunId = runId;
      if (!currentRunId) {
        const sumRes = await fetch('/api/simulations/latest');
        if (sumRes.ok) {
          const sum = await sumRes.json();
          currentRunId = sum.run_id;
          setRunId(currentRunId);
          // If simulation was fresh with 0 packets processed, evaluate them all so the log is full with 100 packets!
          if (sum.processed_packets < 100) {
            await fetch(`/api/simulations/${currentRunId}/step?batch_size=100`, { method: 'POST' });
          }
        }
      }

      if (currentRunId) {
        let url = `/api/simulations/${currentRunId}/packets?page=${page}&limit=${pageSize}`;
        if (filterOutcome !== 'ALL') url += `&filter_outcome=${filterOutcome}`;
        if (search.trim()) url += `&search=${encodeURIComponent(search.trim())}`;

        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          setPackets(data.packets);
          setTotal(data.total);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  const handleRowClick = (pkt) => {
    setSelectedRecord(pkt);
  };

  const handleRowDoubleClick = (pkt) => {
    inspectPacket(pkt);
  };

  return (
    <div className="space-y-6">
      {/* Search and Filters Bar */}
      <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex-1 max-w-md relative">
            <Search className="w-4 h-4 text-appText-muted absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              placeholder="Search by IP, port, packet ID, reason..."
              className="w-full bg-canvas border border-appBorder rounded-md pl-9 pr-3 py-1.5 text-xs text-appText focus:outline-none focus:ring-1 focus:ring-brown font-medium"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Outcome Filter */}
            <div className="flex items-center gap-1 bg-canvas p-1 rounded-md border border-appBorder text-xs">
              <span className="text-[11px] font-semibold text-appText-muted px-2">Verdict:</span>
              {['ALL', 'ALLOW', 'BLOCK'].map(f => (
                <button
                  key={f}
                  onClick={() => { setFilterOutcome(f); setPage(1); }}
                  className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${
                    filterOutcome === f ? 'bg-peach text-brown' : 'text-appText-muted hover:text-appText'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>

            {/* Page Size */}
            <select
              value={pageSize}
              onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}
              className="bg-canvas border border-appBorder rounded-md px-2.5 py-1.5 text-xs text-appText"
            >
              <option value={10}>10 per page</option>
              <option value={25}>25 per page</option>
              <option value={50}>50 per page</option>
              <option value={100}>100 per page</option>
            </select>

            {runId && (
              <a
                href={`/api/export/${runId}/csv`}
                download
                className="flex items-center gap-1.5 px-3 py-1.5 bg-canvas hover:bg-stone/20 text-brown border border-appBorder text-xs font-medium rounded-md transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export CSV</span>
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Main Table and Detail Slide-Over */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Table Container (8 or 12 cols depending on drawer) */}
        <div className={`${selectedRecord ? 'lg:col-span-8' : 'lg:col-span-12'} bg-surface border border-appBorder rounded-xl shadow-xs overflow-hidden transition-all`}>
          <div className="px-5 py-3.5 bg-canvas border-b border-appBorder flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ScrollText className="w-4 h-4 text-brown" />
              <h3 className="font-bold text-sm text-brown">Evaluated Traffic Audit Log</h3>
            </div>
            <span className="text-xs text-appText-muted font-mono">
              Total {total} synthetic records
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse font-mono">
              <thead className="bg-canvas/50 border-b border-appBorder text-appText-muted uppercase tracking-wider text-[11px] font-sans">
                <tr>
                  <th className="py-2.5 px-3.5">#</th>
                  <th className="py-2.5 px-3.5">Packet ID</th>
                  <th className="py-2.5 px-3.5">Source → Destination</th>
                  <th className="py-2.5 px-3.5">Proto</th>
                  <th className="py-2.5 px-3.5 font-sans">Decision</th>
                  <th className="py-2.5 px-3.5 font-sans">Matched Rule / Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-appBorder">
                {packets.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="py-12 text-center text-appText-muted font-sans text-xs">
                      {loading ? 'Loading packet stream...' : 'No packets match your search filters.'}
                    </td>
                  </tr>
                ) : (
                  packets.map((rec) => (
                    <tr
                      key={rec.packet_id}
                      onClick={() => handleRowClick(rec)}
                      onDoubleClick={() => handleRowDoubleClick(rec)}
                      className={`cursor-pointer transition-colors ${
                        selectedRecord?.packet_id === rec.packet_id
                          ? 'bg-peach/30'
                          : 'hover:bg-canvas'
                      }`}
                      title="Click to view details; double-click for raw wire dump"
                    >
                      <td className="py-2.5 px-3.5 text-appText-muted">{rec.sequence}</td>
                      <td className="py-2.5 px-3.5 font-bold text-brown">{rec.packet_id}</td>
                      <td className="py-2.5 px-3.5 text-appText">
                        {rec.packet.source_ip}:{rec.packet.source_port} → {rec.packet.destination_ip}:{rec.packet.port}
                      </td>
                      <td className="py-2.5 px-3.5 text-taupe">{rec.packet.protocol}</td>
                      <td className="py-2.5 px-3.5 font-sans">
                        <OutcomeBadge action={rec.action} size="sm" />
                      </td>
                      <td className="py-2.5 px-3.5 font-sans text-appText text-xs truncate max-w-xs">
                        {rec.matched_rule_name || rec.reason}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="px-5 py-3.5 bg-canvas border-t border-appBorder flex items-center justify-between text-xs">
            <span className="text-appText-muted">
              Showing page <strong className="text-appText">{page}</strong> of <strong className="text-appText">{totalPages}</strong> ({total} total)
            </span>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="p-1 rounded bg-surface border border-appBorder text-appText-muted hover:text-brown disabled:opacity-30"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="p-1 rounded bg-surface border border-appBorder text-appText-muted hover:text-brown disabled:opacity-30"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Selected Packet Inspection Slide-Over / Card */}
        {selectedRecord && (
          <div className="lg:col-span-4 bg-surface border border-stone rounded-xl p-5 shadow-sm space-y-4 animate-in fade-in sticky top-6">
            <div className="flex items-center justify-between border-b border-appBorder pb-3">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-brown" />
                <h4 className="font-bold text-sm text-brown">Packet Inspector</h4>
                <span className="font-mono text-xs text-appText-muted">({selectedRecord.packet_id})</span>
              </div>
              <button
                onClick={() => setSelectedRecord(null)}
                className="p-1 hover:bg-canvas rounded text-appText-muted"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-canvas rounded-lg border border-appBorder space-y-1.5 font-mono">
                <div className="flex justify-between">
                  <span className="text-appText-muted font-sans">Source:</span>
                  <span className="font-bold text-appText">{selectedRecord.packet.source_ip}:{selectedRecord.packet.source_port}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-appText-muted font-sans">Destination:</span>
                  <span className="font-bold text-appText">{selectedRecord.packet.destination_ip}:{selectedRecord.packet.port}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-appText-muted font-sans">Protocol:</span>
                  <span className="font-bold text-taupe">{selectedRecord.packet.protocol}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-appText-muted font-sans">Direction:</span>
                  <span className="text-brown font-sans font-medium">{selectedRecord.packet.direction}</span>
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-[11px] font-bold text-appText-muted uppercase">Verdict</span>
                <div className="flex items-center gap-2">
                  <OutcomeBadge action={selectedRecord.action} size="md" />
                  {selectedRecord.connection_state && (
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-peach/40 text-brown font-bold border border-peach">
                      {selectedRecord.connection_state}
                    </span>
                  )}
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-[11px] font-bold text-appText-muted uppercase">Matched Policy</span>
                <p className="text-appText font-medium bg-canvas p-2 rounded border border-appBorder">
                  {selectedRecord.matched_rule_name || 'Implicit Default Drop'}
                </p>
              </div>

              <div className="space-y-1">
                <span className="text-[11px] font-bold text-appText-muted uppercase">Plain-English Reason</span>
                <p className="text-appText-muted bg-canvas p-2.5 rounded border border-appBorder leading-relaxed">
                  {selectedRecord.reason}
                </p>
              </div>

              <div className="pt-2">
                <button
                  onClick={() => inspectPacket(selectedRecord)}
                  className="w-full py-2 bg-brown hover:bg-brown-light text-white text-xs font-semibold rounded-md shadow-xs transition-colors flex items-center justify-center gap-1.5"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Open Raw Wire Disassembly</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
