import React from 'react';
import { CheckCircle2, XCircle, Clock } from 'lucide-react';

export default function OutcomeBadge({ action, size = 'md' }) {
  if (action === 'ALLOW') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-allowed-soft text-allowed border border-allowed-border ${
        size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs'
      }`}>
        <CheckCircle2 className={size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
        ALLOWED
      </span>
    );
  }

  if (action === 'BLOCK') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-blocked-soft text-blocked border border-blocked-border ${
        size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs'
      }`}>
        <XCircle className={size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
        BLOCKED
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium rounded-md bg-stone/20 text-appText-muted border border-stone/40 ${
      size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs'
    }`}>
      <Clock className={size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
      {action || 'PENDING'}
    </span>
  );
}
