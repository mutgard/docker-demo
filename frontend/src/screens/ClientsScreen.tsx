import { useState, useEffect } from 'react';
import { api } from '../api';
import type { Client } from '../types';
import { Badge } from '../components/Badge';

interface Props { onSelect: (c: Client) => void; animClass: string; }

function ClientCard({ c, idx, onSelect }: { c: Client; idx: number; onSelect: () => void }) {
  const past = c.days_until < 0;
  const fabricSummary = c.fabrics.length > 0 ? `${c.fabrics.length} teles` : '—';
  return (
    <div className="tap" onClick={onSelect} style={{
      background: 'var(--bg-card)', border: '1px solid var(--line)', borderRadius: 8,
      padding: '13px 13px 11px', marginBottom: 8,
      animation: `fadeUp .3s ease ${idx * .04}s both`,
    }}>
      <div style={{ display: 'flex', gap: 11, alignItems: 'flex-start', marginBottom: 10 }}>
        <div style={{
          width: 44, height: 44, borderRadius: '50%', background: 'var(--line-l)', flexShrink: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'var(--font-d)', fontSize: 20, fontStyle: 'italic', color: 'var(--ink-3)',
          border: '1px solid var(--line)',
        }}>
          {c.name[0]}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontFamily: 'var(--font-u)', fontSize: 15, fontWeight: 500, color: 'var(--ink-1)', letterSpacing: '-.1px' }}>{c.name}</div>
          <div style={{ fontFamily: 'var(--font-m)', fontSize: 10, color: 'var(--ink-3)', marginTop: 2 }}>{c.garment}</div>
        </div>
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontFamily: 'var(--font-m)', fontSize: 11, fontWeight: 500, color: 'var(--ink-2)' }}>{c.wedding_date}</div>
          <div style={{ fontFamily: 'var(--font-m)', fontSize: 10, color: past ? 'var(--ink-4)' : 'var(--ink-3)', marginTop: 1 }}>
            {past ? `fa ${Math.abs(c.days_until)}d` : `d−${c.days_until}`}
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
        <Badge status={c.status} />
        {fabricSummary !== '—' && (
          <span style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)', textTransform: 'uppercase', letterSpacing: '.4px' }}>{fabricSummary}</span>
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
      <div style={{ padding: '10px 20px 0', flexShrink: 0 }}>
        <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--ink-3)', marginBottom: 1 }}>Atelier</div>
        <div style={{ fontFamily: 'var(--font-d)', fontSize: 34, fontWeight: 400, color: 'var(--ink-1)', letterSpacing: '-.3px', lineHeight: 1.1, marginBottom: 12 }}>Clientes</div>
        <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8, background: 'var(--bg-card)', border: '1px solid var(--line)', padding: '7px 12px', borderRadius: 6 }}>
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="var(--ink-3)" strokeWidth="1.5"><circle cx="5.5" cy="5.5" r="4"/><path d="M9 9l3 3" strokeLinecap="round"/></svg>
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Cerca per nom…" style={{ border: 'none', background: 'none', fontFamily: 'var(--font-u)', fontSize: 13, color: 'var(--ink-2)', outline: 'none', width: '100%' }}/>
          </div>
          <div style={{ width: 34, height: 34, border: '1px solid var(--line)', background: 'var(--bg-card)', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 6, color: 'var(--ink-2)', cursor: 'pointer', flexShrink: 0 }}>
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M7.5 2.5v10M2.5 7.5h10" strokeLinecap="round"/></svg>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 5, overflowX: 'auto', paddingBottom: 10, scrollbarWidth: 'none' }}>
          {chips.map(f => {
            const on = filter === f.id;
            return (
              <button key={f.id} onClick={() => setFilter(f.id)} style={{
                padding: '3px 10px', fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '.5px',
                textTransform: 'uppercase', border: '1px solid', flexShrink: 0,
                borderColor: on ? 'var(--ink-1)' : 'var(--line)',
                background: on ? 'var(--ink-1)' : 'transparent',
                color: on ? 'var(--bg-card)' : 'var(--ink-3)',
                borderRadius: 2, transition: 'all .15s ease',
              }}>
                {f.l}
              </button>
            );
          })}
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 20px 8px', borderBottom: '1px solid var(--line-l)', borderTop: '1px solid var(--line-l)', flexShrink: 0 }}>
        <span style={{ fontFamily: 'var(--font-m)', fontSize: 9, letterSpacing: '.4px', textTransform: 'uppercase', color: 'var(--ink-3)' }}>Data boda ↑</span>
        <span style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-4)' }}>{list.length} clientes</span>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '10px 14px 16px' }}>
        {list.map((c, i) => <ClientCard key={c.id} c={c} idx={i} onSelect={() => onSelect(c)} />)}
        {list.length === 0 && (
          <div style={{ textAlign: 'center', padding: '48px 0', fontFamily: 'var(--font-d)', fontSize: 18, fontStyle: 'italic', color: 'var(--ink-3)' }}>Cap resultat</div>
        )}
      </div>
    </div>
  );
}
