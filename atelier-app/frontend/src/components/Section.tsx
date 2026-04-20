import React from 'react';

export function Section({ title, action, children }: { title: string; action?: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 26 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <span style={{
          fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '2px',
          textTransform: 'uppercase', color: 'var(--ink-3)',
        }}>{title}</span>
        {action && (
          <span style={{ fontFamily: 'var(--font-m)', fontSize: 8, color: 'var(--accent)', cursor: 'pointer', letterSpacing: '.5px' }}>{action}</span>
        )}
      </div>
      <div style={{ borderTop: '1px solid var(--line)', paddingTop: 2 }}>{children}</div>
    </div>
  );
}
