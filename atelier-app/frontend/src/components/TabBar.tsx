import React from 'react';

type Tab = 'clients' | 'fabrics' | 'shop';
interface Props { active: Tab; onChange: (t: Tab) => void; }

export function TabBar({ active, onChange }: Props) {
  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    {
      id: 'clients', label: 'Clientes',
      icon: (
        <svg width="21" height="21" viewBox="0 0 21 21" fill="none" stroke="currentColor" strokeWidth="1.4">
          <circle cx="8.5" cy="7.5" r="3.2"/>
          <path d="M2 19c0-3.59 2.91-6.5 6.5-6.5s6.5 2.91 6.5 6.5" strokeLinecap="round"/>
          <circle cx="16" cy="6.5" r="2.3"/>
          <path d="M18.5 17.5c0-2.76-.9-4.5 0-4.5" strokeLinecap="round"/>
        </svg>
      ),
    },
    {
      id: 'fabrics', label: 'Teles',
      icon: (
        <svg width="21" height="21" viewBox="0 0 21 21" fill="none" stroke="currentColor" strokeWidth="1.4">
          <path d="M4.5 4.5c0 0 4 3.2 6 0s6 0 6 0v12c0 0-4-3.2-6 0s-6 0-6 0z"/>
        </svg>
      ),
    },
    {
      id: 'shop', label: 'Comprar',
      icon: (
        <svg width="21" height="21" viewBox="0 0 21 21" fill="none" stroke="currentColor" strokeWidth="1.4">
          <path d="M3.5 5.5h1.5l2.5 8.5h9l2-7H7.5" strokeLinecap="round" strokeLinejoin="round"/>
          <circle cx="9.5" cy="17" r="1.3" fill="currentColor" stroke="none"/>
          <circle cx="14.5" cy="17" r="1.3" fill="currentColor" stroke="none"/>
        </svg>
      ),
    },
  ];

  return (
    <div style={{
      height: 72, flexShrink: 0, borderTop: '1px solid var(--line)',
      background: 'rgba(253,250,245,.97)', backdropFilter: 'blur(8px)',
      display: 'flex', alignItems: 'flex-start', paddingTop: 6,
    }}>
      {tabs.map(t => {
        const on = t.id === active;
        return (
          <button key={t.id} onClick={() => onChange(t.id)} style={{
            flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3,
            background: 'none', border: 'none', padding: '6px 0 14px',
            color: on ? 'var(--ink-1)' : 'var(--ink-4)', transition: 'color .15s ease',
          }}>
            {t.icon}
            <span style={{
              fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '.5px',
              textTransform: 'uppercase', fontWeight: on ? 500 : 400,
            }}>{t.label}</span>
            {on && (
              <div style={{
                position: 'absolute', top: 72, width: 28, height: 2,
                background: 'var(--ink-1)', borderRadius: 1, marginTop: -68,
              }}/>
            )}
          </button>
        );
      })}
    </div>
  );
}
