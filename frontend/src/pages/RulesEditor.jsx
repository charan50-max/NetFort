import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  RotateCcw, 
  ArrowUp, 
  ArrowDown, 
  Trash2, 
  Edit2, 
  AlertTriangle, 
  Check, 
  X, 
  SlidersHorizontal,
  Bookmark
} from 'lucide-react';
import OutcomeBadge from '../components/common/OutcomeBadge';

export default function RulesEditor() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    source_ip: '*',
    destination_ip: '*',
    port: '*',
    protocol: 'ANY',
    action: 'BLOCK',
    enabled: true
  });
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const res = await fetch('/api/rules');
      if (res.ok) {
        setRules(await res.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAdd = () => {
    setEditingIndex(null);
    setFormData({
      name: '',
      description: '',
      source_ip: '*',
      destination_ip: '*',
      port: '*',
      protocol: 'TCP',
      action: 'ALLOW',
      enabled: true
    });
    setErrorMsg('');
    setModalOpen(true);
  };

  const handleOpenEdit = (rule, index) => {
    setEditingIndex(index);
    setFormData({ ...rule });
    setErrorMsg('');
    setModalOpen(true);
  };

  const handleSaveForm = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    // Inline validation
    if (!formData.name.trim()) {
      setErrorMsg('Rule name is required.');
      return;
    }

    try {
      if (editingIndex !== null) {
        // Update existing rule
        const updated = [...rules];
        updated[editingIndex] = { ...formData, rule_id: rules[editingIndex].rule_id };
        const res = await fetch('/api/rules', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ rules: updated })
        });
        if (!res.ok) {
          const err = await res.json();
          setErrorMsg(err.detail || 'Failed to update rules.');
          return;
        }
        setRules(updated);
        setSuccessMsg('Rule updated successfully.');
      } else {
        // Add new rule
        const res = await fetch('/api/rules', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });
        if (!res.ok) {
          const err = await res.json();
          setErrorMsg(err.detail || 'Failed to create rule.');
          return;
        }
        await fetchRules();
        setSuccessMsg('New rule added successfully.');
      }
      setModalOpen(false);
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setErrorMsg('Network error.');
    }
  };

  const handleDelete = async (index) => {
    if (!window.confirm(`Are you sure you want to delete rule #${index + 1}?`)) return;
    try {
      const res = await fetch(`/api/rules/${index}`, { method: 'DELETE' });
      if (res.ok) {
        await fetchRules();
        setSuccessMsg('Rule deleted.');
        setTimeout(() => setSuccessMsg(''), 3000);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleMoveUp = async (index) => {
    try {
      const res = await fetch(`/api/rules/move-up/${index}`, { method: 'POST' });
      if (res.ok) await fetchRules();
    } catch (err) {
      console.error(err);
    }
  };

  const handleMoveDown = async (index) => {
    try {
      const res = await fetch(`/api/rules/move-down/${index}`, { method: 'POST' });
      if (res.ok) await fetchRules();
    } catch (err) {
      console.error(err);
    }
  };

  const handlePreset = async (presetName) => {
    try {
      const res = await fetch(`/api/rules/presets/${presetName}`, { method: 'POST' });
      if (res.ok) {
        await fetchRules();
        setSuccessMsg(`Preset '${presetName}' loaded.`);
        setTimeout(() => setSuccessMsg(''), 3000);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleResetDefaults = async () => {
    if (!window.confirm('Reset all rules back to baseline educational defaults?')) return;
    try {
      const res = await fetch('/api/rules/reset', { method: 'POST' });
      if (res.ok) {
        await fetchRules();
        setSuccessMsg('Rules restored to baseline.');
        setTimeout(() => setSuccessMsg(''), 3000);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Action Bar & Presets */}
      <div className="bg-surface border border-appBorder rounded-xl p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="font-bold text-base text-brown">Firewall Rule Policies</h2>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-peach text-brown border border-peach-dark">
              FIRST MATCH WINS
            </span>
          </div>
          <p className="text-xs text-appText-muted mt-0.5">
            Packets traverse rules sequentially from Priority #1 downwards.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Preset Buttons */}
          <div className="flex items-center gap-1 bg-canvas p-1 rounded-md border border-appBorder text-xs">
            <span className="text-[11px] text-appText-muted font-medium px-2 flex items-center gap-1">
              <Bookmark className="w-3 h-3" /> Presets:
            </span>
            <button
              onClick={() => handlePreset('balanced')}
              className="px-2 py-1 hover:bg-peach/50 rounded text-brown font-medium"
            >
              Balanced
            </button>
            <button
              onClick={() => handlePreset('strict')}
              className="px-2 py-1 hover:bg-peach/50 rounded text-brown font-medium"
            >
              Strict
            </button>
            <button
              onClick={() => handlePreset('order_demo')}
              className="px-2 py-1 hover:bg-peach/50 rounded text-brown font-medium"
            >
              Order Shadow
            </button>
          </div>

          <button
            onClick={handleOpenAdd}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-brown hover:bg-brown-light text-white text-xs font-semibold rounded-md shadow-xs transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Rule</span>
          </button>

          <button
            onClick={handleResetDefaults}
            className="flex items-center gap-1.5 px-3 py-2 bg-canvas hover:bg-stone/20 text-appText-muted hover:text-brown border border-appBorder text-xs font-medium rounded-md transition-colors"
            title="Restore default demo rules"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Restore Demo</span>
          </button>
        </div>
      </div>

      {/* Notifications */}
      {successMsg && (
        <div className="p-3 bg-allowed-soft text-allowed border border-allowed-border rounded-lg text-xs font-medium flex items-center gap-2 animate-in fade-in">
          <Check className="w-4 h-4" /> {successMsg}
        </div>
      )}

      {/* Ordered Rules Table */}
      <div className="bg-surface border border-appBorder rounded-xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-canvas border-b border-appBorder text-appText-muted uppercase tracking-wider text-[11px]">
              <tr>
                <th className="py-3 px-3.5 w-16">Priority</th>
                <th className="py-3 px-3.5">Rule Name & Details</th>
                <th className="py-3 px-3.5 font-mono">Source IP</th>
                <th className="py-3 px-3.5 font-mono">Dest IP</th>
                <th className="py-3 px-3.5">Protocol</th>
                <th className="py-3 px-3.5 font-mono">Port</th>
                <th className="py-3 px-3.5">Action</th>
                <th className="py-3 px-3.5 text-right">Reorder & Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-appBorder font-mono">
              {rules.map((rule, idx) => (
                <tr key={rule.rule_id || idx} className="hover:bg-canvas/80 transition-colors">
                  <td className="py-3 px-3.5 font-bold text-brown">
                    <span className="w-6 h-6 rounded-full bg-peach/60 flex items-center justify-center font-bold text-xs">
                      {idx + 1}
                    </span>
                  </td>
                  <td className="py-3 px-3.5 font-sans">
                    <div className="font-bold text-appText">{rule.name}</div>
                    {rule.description && (
                      <div className="text-[11px] text-appText-muted">{rule.description}</div>
                    )}
                  </td>
                  <td className="py-3 px-3.5 text-appText">{rule.source_ip}</td>
                  <td className="py-3 px-3.5 text-appText">{rule.destination_ip}</td>
                  <td className="py-3 px-3.5 font-sans font-bold text-taupe">{rule.protocol}</td>
                  <td className="py-3 px-3.5 text-appText">{rule.port}</td>
                  <td className="py-3 px-3.5 font-sans">
                    <OutcomeBadge action={rule.action} size="sm" />
                  </td>
                  <td className="py-3 px-3.5 text-right font-sans">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => handleMoveUp(idx)}
                        disabled={idx === 0}
                        className="p-1 hover:bg-stone/20 rounded text-appText-muted hover:text-brown disabled:opacity-20"
                        title="Move Up"
                      >
                        <ArrowUp className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleMoveDown(idx)}
                        disabled={idx === rules.length - 1}
                        className="p-1 hover:bg-stone/20 rounded text-appText-muted hover:text-brown disabled:opacity-20"
                        title="Move Down"
                      >
                        <ArrowDown className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleOpenEdit(rule, idx)}
                        className="p-1 hover:bg-peach/40 rounded text-taupe hover:text-brown ml-1"
                        title="Edit Rule"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDelete(idx)}
                        className="p-1 hover:bg-blocked-soft rounded text-stone hover:text-blocked"
                        title="Delete Rule"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add / Edit Rule Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
          <div className="bg-surface border border-stone w-full max-w-lg rounded-xl shadow-xl overflow-hidden animate-in fade-in">
            <div className="px-6 py-4 bg-canvas border-b border-appBorder flex items-center justify-between">
              <h3 className="font-bold text-base text-brown">
                {editingIndex !== null ? `Edit Rule #${editingIndex + 1}` : 'Add New Firewall Rule'}
              </h3>
              <button onClick={() => setModalOpen(false)} className="p-1 text-appText-muted">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveForm} className="p-6 space-y-4 text-xs">
              {errorMsg && (
                <div className="p-3 bg-blocked-soft text-blocked border border-blocked-border rounded-md">
                  {errorMsg}
                </div>
              )}

              <div>
                <label className="font-semibold text-appText-muted block mb-1">Rule Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Allow Web Browsing"
                  className="w-full bg-canvas border border-appBorder rounded-md px-3 py-2 text-appText focus:outline-none focus:ring-1 focus:ring-brown font-medium"
                />
              </div>

              <div>
                <label className="font-semibold text-appText-muted block mb-1">Description (Optional)</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="e.g. Permit internal client requests to web port 80"
                  className="w-full bg-canvas border border-appBorder rounded-md px-3 py-2 text-appText focus:outline-none focus:ring-1 focus:ring-brown"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-appText-muted block mb-1">Source IP / CIDR (* for Any)</label>
                  <input
                    type="text"
                    required
                    value={formData.source_ip}
                    onChange={(e) => setFormData({ ...formData, source_ip: e.target.value })}
                    className="w-full bg-canvas border border-appBorder rounded-md px-3 py-2 font-mono text-appText"
                  />
                </div>
                <div>
                  <label className="font-semibold text-appText-muted block mb-1">Destination IP / CIDR</label>
                  <input
                    type="text"
                    required
                    value={formData.destination_ip}
                    onChange={(e) => setFormData({ ...formData, destination_ip: e.target.value })}
                    className="w-full bg-canvas border border-appBorder rounded-md px-3 py-2 font-mono text-appText"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="font-semibold text-appText-muted block mb-1">Protocol</label>
                  <select
                    value={formData.protocol}
                    onChange={(e) => setFormData({ ...formData, protocol: e.target.value })}
                    className="w-full bg-canvas border border-appBorder rounded-md px-3 py-2 text-appText"
                  >
                    <option value="ANY">ANY</option>
                    <option value="TCP">TCP</option>
                    <option value="UDP">UDP</option>
                    <option value="ICMP">ICMP</option>
                  </select>
                </div>

                <div>
                  <label className="font-semibold text-appText-muted block mb-1">Port (* or 0-65535)</label>
                  <input
                    type="text"
                    required
                    disabled={formData.protocol === 'ICMP'}
                    value={formData.protocol === 'ICMP' ? '*' : formData.port}
                    onChange={(e) => setFormData({ ...formData, port: e.target.value })}
                    className="w-full bg-canvas border border-appBorder rounded-md px-3 py-2 font-mono text-appText disabled:opacity-40"
                  />
                </div>

                <div>
                  <label className="font-semibold text-appText-muted block mb-1">Action</label>
                  <select
                    value={formData.action}
                    onChange={(e) => setFormData({ ...formData, action: e.target.value })}
                    className="w-full bg-canvas border border-appBorder rounded-md px-3 py-2 text-appText font-bold"
                  >
                    <option value="ALLOW">ALLOW</option>
                    <option value="BLOCK">BLOCK</option>
                  </select>
                </div>
              </div>

              <div className="pt-4 border-t border-appBorder flex items-center justify-end gap-2.5">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 bg-canvas hover:bg-stone/20 text-appText-muted rounded-md border border-appBorder"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-brown hover:bg-brown-light text-white font-semibold rounded-md shadow-xs"
                >
                  Save Policy Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
