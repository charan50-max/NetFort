import React, { useState } from 'react';
import { X, Copy, Check, Terminal, Shield, ArrowRight, Activity, FileText } from 'lucide-react';

export default function PacketInspectorModal({ packet, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!packet) return null;

  // Normalize packet attributes if wrapped in an event record
  const p = packet.packet || packet;
  const rawText = p.raw_format || packet.raw_format || `Frame ${p.sequence || 1}: ${p.protocol} ${p.source_ip}:${p.source_port} -> ${p.destination_ip}:${p.port}`;
  const action = packet.action || p.action;
  const reason = packet.reason || p.reason;
  const ruleName = packet.matched_rule_name || p.matched_rule_name;
  const connectionState = packet.connection_state || p.connection_state;

  const handleCopy = () => {
    navigator.clipboard.writeText(rawText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="bg-surface border border-stone w-full max-w-3xl rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-canvas border-b border-appBorder px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="p-2 rounded-lg bg-peach/40 text-brown border border-peach">
              <Terminal className="w-5 h-5" />
            </span>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-semibold text-lg text-brown">Raw Packet Inspection</h3>
                <span className="px-2 py-0.5 text-xs font-mono font-medium bg-stone/30 text-appText rounded border border-stone">
                  {p.packet_id || 'PKT-RAW'}
                </span>
                {action && (
                  <span className={`px-2 py-0.5 text-xs font-bold rounded ${
                    action === 'ALLOW' 
                      ? 'bg-allowed-soft text-allowed border border-allowed-border' 
                      : 'bg-blocked-soft text-blocked border border-blocked-border'
                  }`}>
                    {action}
                  </span>
                )}
              </div>
              <p className="text-xs text-appText-muted mt-0.5">
                Original wire data and protocol dissection (Double-Click View)
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-md hover:bg-stone/30 text-appText-muted hover:text-appText transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-5">
          {/* 4-Tuple & Header Info Card */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-canvas p-4 rounded-lg border border-appBorder">
            <div>
              <span className="text-[11px] font-medium text-appText-muted uppercase tracking-wider block">Source</span>
              <span className="font-mono text-sm font-semibold text-appText block mt-0.5">
                {p.source_ip}{p.source_port ? `:${p.source_port}` : ''}
              </span>
            </div>
            <div>
              <span className="text-[11px] font-medium text-appText-muted uppercase tracking-wider block">Destination</span>
              <span className="font-mono text-sm font-semibold text-appText block mt-0.5">
                {p.destination_ip}:{p.port}
              </span>
            </div>
            <div>
              <span className="text-[11px] font-medium text-appText-muted uppercase tracking-wider block">Protocol / Flags</span>
              <span className="font-mono text-sm font-semibold text-appText block mt-0.5">
                {p.protocol} {p.tcp_flags ? `[${p.tcp_flags}]` : ''}
              </span>
            </div>
            <div>
              <span className="text-[11px] font-medium text-appText-muted uppercase tracking-wider block">Flow Direction</span>
              <span className="text-xs font-medium px-2 py-0.5 rounded bg-peach/50 text-brown inline-block mt-0.5 border border-peach">
                {p.direction || 'OUTBOUND'}
              </span>
            </div>
          </div>

          {/* Purpose & Real World Meaning */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-appText-muted uppercase tracking-wider flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-taupe" />
              Simulated Traffic Purpose
            </h4>
            <div className="p-3 bg-peach/15 border border-peach/50 rounded-lg">
              <p className="font-medium text-sm text-brown">{p.purpose || 'Synthetic packet stream'}</p>
              {p.explanation && (
                <p className="text-xs text-appText-muted mt-1 leading-relaxed">{p.explanation}</p>
              )}
            </div>
          </div>

          {/* Decision Breakdown (if evaluated) */}
          {(action || reason) && (
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-appText-muted uppercase tracking-wider flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-taupe" />
                Firewall Evaluation Outcome
              </h4>
              <div className="p-3.5 bg-surface border border-appBorder rounded-lg space-y-1.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-appText-muted">Decision:</span>
                  <span className={`font-bold ${action === 'ALLOW' ? 'text-allowed' : 'text-blocked'}`}>
                    {action || 'PENDING'}
                  </span>
                </div>
                {ruleName && (
                  <div className="flex items-center justify-between">
                    <span className="text-appText-muted">Matched Policy:</span>
                    <span className="font-medium text-brown">{ruleName}</span>
                  </div>
                )}
                {connectionState && (
                  <div className="flex items-center justify-between">
                    <span className="text-appText-muted">Connection State:</span>
                    <span className="font-mono text-taupe font-medium">{connectionState}</span>
                  </div>
                )}
                {reason && (
                  <div className="pt-1 border-t border-appBorder/50 text-appText">
                    <span className="text-appText-muted font-medium">Reason: </span>
                    {reason}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Original Wire Raw Format (Wireshark / tcpdump) */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold text-appText-muted uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-taupe" />
                Original Packet Wire Representation
              </h4>
              <button
                onClick={handleCopy}
                className="text-xs flex items-center gap-1 text-taupe hover:text-brown font-medium px-2 py-1 rounded bg-stone/20 hover:bg-stone/40 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-allowed" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Copied' : 'Copy Raw Wire'}
              </button>
            </div>
            <pre className="bg-[#1E1E1E] text-[#D4D4D4] p-4 rounded-lg font-mono text-xs leading-relaxed overflow-x-auto border border-stone/50 shadow-inner max-h-56">
              <code>{rawText}</code>
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-canvas border-t border-appBorder px-6 py-3.5 flex items-center justify-between">
          <span className="text-xs text-appText-muted">
            Tip: You can double-click any packet row or tile anywhere in NetFort to inspect this view.
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-brown hover:bg-brown-light text-white text-xs font-medium rounded-md shadow-sm transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
