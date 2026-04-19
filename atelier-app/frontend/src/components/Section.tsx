import React from 'react';

export function Section({ title, action, children }: { title: string; action?: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 22 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 7 }}>
        <span style={{
          fontFamily: 'var(--font-m)', fontSize: 9, letterSpacing: '1px',
          textTransform: 'uppercase', color: 'var(--ink-3)',
        }}>{title}</span>
        {action && (
          <span style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--accent)', cursor: 'pointer' }}>{action}</span>
        )}
      </div>
      <div style={{ borderTop: '1px solid var(--line)', paddingTop: 10 }}>{children}</div>
    </div>
  );
}
