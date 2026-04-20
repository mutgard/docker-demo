import { useState, useEffect } from 'react';
import { api } from '../api';
import type { Client } from '../types';
import { Badge } from '../components/Badge';

interface Props { onSelect: (c: Client) => void; animClass: string; }

function ClientCard({ c, idx, onSelect }: { c: Client; idx: number; onSelect: () => void }) {
  const past = c.days_until < 0;
  const soon = !past && c.days_until <= 30;
  return (
    <div className="tap" onClick={onSelect} style={{
      background: 'var(--bg-card)', border: '1px solid var(--line)', borderRadius: 4,
      padding: '14px 16px 12px', marginBottom: 6,
      animation: `fadeUp .32s ease ${idx * .04}s both`,
      transition: 'border-color .15s ease',
    }}>
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', marginBottom: 10 }}>
        <div style={{
          width: 42, height: 42, borderRadius: '50%', flexShrink: 0,
          background: 'linear-gradient(135deg, var(--line) 0%, var(--bg-app) 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'var(--font-d)', fontSize: 19, fontStyle: 'italic', color: 'var(--ink-3)',
          border: '1px solid var(--line)',
        }}>
          {c.name[0]}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontFamily: 'var(--font-u)', fontSize: 14, fontWeight: 400, color: 'var(--ink-1)', letterSpacing: '-.1px' }}>{c.name}</div>
          <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)', marginTop: 3, letterSpacing: '.3px' }}>{c.garment}</div>
        </div>
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontFamily: 'var(--font-m)', fontSize: 10, color: 'var(--ink-2)' }}>{c.wedding_date}</div>
          <div style={{
            fontFamily: 'var(--font-m)', fontSize: 9, marginTop: 2,
            color: past ? 'var(--ink-4)' : soon ? 'var(--accent)' : 'var(--ink-3)',
          }}>
            {past ? `fa ${Math.abs(c.days_until)}d` : `d−${c.days_until}`}
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
        <Badge status={c.status} />
        {c.fabrics.length > 0 && (
          <span style={{ fontFamily: 'var(--font-m)', fontSize: 8, color: 'var(--ink-4)', textTransform: 'uppercase', letterSpacing: '.6px' }}>{c.fabrics.length} teles</span>
        )}
      </div>
    </div>
  );
}

export function ClientsScreen({ onSelect, animClass }: Props) {
  const [clients, setClients] = useState<Client[]>([]);
  const [filter, setFilter] = useState('totes');
  const [search, setSearch] = useState('');

  useEffect(() => { api.listClients().then(setClients); }, []);

  const chips = [
    { id: 'totes', l: 'Totes' }, { id: 'prospect', l: 'Prospect' },
    { id: 'sense-paga', l: 'Sense paga' }, { id: 'clienta', l: 'Clienta' }, { id: 'entregada', l: 'Entregada' },
  ];

  const list = clients
    .filter(c => {
      const okF = filter === 'totes' || c.status === filter;
      const okS = !search || c.name.toLowerCase().includes(search.toLowerCase());
      return okF && okS;
    })
    .sort((a, b) => a.days_until - b.days_until);

  return (
    <div className={animClass} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg-app)' }}>

      {/* Header */}
      <div style={{ padding: '20px 24px 0', flexShrink: 0 }}>
        <div style={{ fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '2.5px', textTransform: 'uppercase', color: 'var(--ink-4)', marginBottom: 4 }}>Atelier</div>
        <div style={{ fontFamily: 'var(--font-d)', fontSize: 'clamp(34px, 4vw, 48px)', fontWeight: 300, fontStyle: 'italic', color: 'var(--ink-1)', lineHeight: 1, marginBottom: 18 }}>Clientes</div>

        {/* Search row */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8, background: 'var(--bg-card)', border: '1px solid var(--line)', padding: '8px 12px', borderRadius: 3 }}>
            <svg width="12" height="12" viewBox="0 0 13 13" fill="none" stroke="var(--ink-3)" strokeWidth="1.5">
              <circle cx="5.5" cy="5.5" r="4"/><path d="M9 9l3 3" strokeLinecap="round"/>
            </svg>
            <input
              value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Cerca per nom…"
              style={{ border: 'none', background: 'none', fontFamily: 'var(--font-u)', fontSize: 13, color: 'var(--ink-2)', outline: 'none', width: '100%' }}
            />
          </div>
          <div style={{ width: 36, height: 36, border: '1px solid var(--line)', background: 'var(--bg-card)', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 3, color: 'var(--ink-3)', cursor: 'pointer', flexShrink: 0 }}>
            <svg width="14" height="14" viewBox="0 0 15 15" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M7.5 2.5v10M2.5 7.5h10" strokeLinecap="round"/></svg>
          </div>
        </div>

        {/* Filter chips */}
        <div style={{ display: 'flex', gap: 5, overflowX: 'auto', paddingBottom: 12, scrollbarWidth: 'none' }}>
          {chips.map(f => {
            const on = filter === f.id;
            return (
              <button key={f.id} onClick={() => setFilter(f.id)} style={{
                padding: '3px 10px', fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '.8px',
                textTransform: 'uppercase', border: '1px solid', flexShrink: 0,
                borderColor: on ? 'var(--accent)' : 'var(--line)',
                background: on ? 'var(--accent)' : 'transparent',
                color: on ? 'var(--bg-app)' : 'var(--ink-3)',
                borderRadius: 2, transition: 'all .15s ease',
              }}>
                {f.l}
              </button>
            );
          })}
        </div>
      </div>

      {/* Sort bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 24px 7px', borderBottom: '1px solid var(--line)', borderTop: '1px solid var(--line)', flexShrink: 0 }}>
        <span style={{ fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '.8px', textTransform: 'uppercase', color: 'var(--ink-4)' }}>Data boda ↑</span>
        <span style={{ fontFamily: 'var(--font-m)', fontSize: 8, color: 'var(--ink-4)', letterSpacing: '.3px' }}>{list.length} clientes</span>
      </div>

      {/* List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '10px 16px 20px' }}>
        {list.map((c, i) => <ClientCard key={c.id} c={c} idx={i} onSelect={() => onSelect(c)} />)}
        {list.length === 0 && (
          <div style={{ textAlign: 'center', padding: '60px 0', fontFamily: 'var(--font-d)', fontSize: 20, fontStyle: 'italic', color: 'var(--ink-4)' }}>Cap resultat</div>
        )}
      </div>
    </div>
  );
}
