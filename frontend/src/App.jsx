import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import { PacketModalProvider } from './context/PacketModalContext';
import Dashboard from './pages/Dashboard';
import LiveSimulation from './pages/LiveSimulation';
import CompareFirewalls from './pages/CompareFirewalls';
import RulesEditor from './pages/RulesEditor';
import MetricsDashboard from './pages/MetricsDashboard';
import PacketLog from './pages/PacketLog';

export default function App() {
  const handleGlobalReset = async () => {
    try {
      await fetch('/api/rules/reset', { method: 'POST' });
      window.location.reload();
    } catch (err) {
      console.error('Reset error:', err);
    }
  };

  return (
    <PacketModalProvider>
      <AppShell onResetDemo={handleGlobalReset}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/simulation" element={<LiveSimulation />} />
          <Route path="/compare" element={<CompareFirewalls />} />
          <Route path="/rules" element={<RulesEditor />} />
          <Route path="/metrics" element={<MetricsDashboard />} />
          <Route path="/packet-log" element={<PacketLog />} />
        </Routes>
      </AppShell>
    </PacketModalProvider>
  );
}
