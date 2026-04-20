import React from 'react';

type Tab = 'clients' | 'fabrics' | 'shop';
interface Props { active: Tab; onChange: (t: Tab) => void; variant: 'bottom' | 'sidebar'; }

export function TabBar({ active, onChange, variant }: Props) {
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

  if (variant === 'sidebar') {
    return (
      <nav className="tab-bar--sidebar" style={{
        width: 200, flexShrink: 0, flexDirection: 'column',
        borderRight: '1px solid var(--line)', background: 'var(--bg-card)',
        overflow: 'hidden',
      }}>
        <div style={{ padding: '28px 20px 24px', borderBottom: '1px solid var(--line-l)' }}>
          <div style={{ fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '2px', textTransform: 'uppercase', color: 'var(--ink-3)', marginBottom: 4 }}>Studio</div>
          <div style={{ fontFamily: 'var(--font-d)', fontSize: 24, fontWeight: 400, fontStyle: 'italic', color: 'var(--ink-1)', lineHeight: 1 }}>Atelier</div>
        </div>
        <div style={{ padding: '12px 0' }}>
          {tabs.map(t => {
            const on = t.id === active;
            return (
              <button key={t.id} onClick={() => onChange(t.id)} className="tap" style={{
                width: '100%', display: 'flex', alignItems: 'center', gap: 12,
                padding: '11px 20px',
                background: on ? 'var(--bg-canvas)' : 'none',
                border: 'none',
                borderLeft: `2px solid ${on ? 'var(--ink-1)' : 'transparent'}`,
                color: on ? 'var(--ink-1)' : 'var(--ink-3)',
                transition: 'all .15s ease', cursor: 'pointer',
              }}>
                {t.icon}
                <span style={{ fontFamily: 'var(--font-m)', fontSize: 9, letterSpacing: '.8px', textTransform: 'uppercase', fontWeight: on ? 500 : 400 }}>{t.label}</span>
              </button>
            );
          })}
        </div>
      </nav>
    );
  }

  return (
    <div className="tab-bar--bottom" style={{
      height: 72, flexShrink: 0, borderTop: '1px solid var(--line)',
      background: 'rgba(253,250,245,.97)', backdropFilter: 'blur(8px)',
      alignItems: 'flex-start', paddingTop: 6,
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
