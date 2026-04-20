import { useState } from 'react';
import type { Client } from '../types';
import { T } from '../tokens';
import { useIsMobile } from '../hooks/useIsMobile';
import { PageHeader } from '../components/PageHeader';
import { Badge, Mono } from '../components/primitives';
import { initials } from '../lib/clientHelpers';

interface Props { clients: Client[]; onOpen: (id: number) => void; }

const CHIPS = [
  { id: 'totes', l: 'Totes' },
  { id: 'prospect', l: 'Prospect' },
  { id: 'sense-paga', l: 'Sense paga' },
  { id: 'clienta', l: 'Clienta' },
  { id: 'entregada', l: 'Entregada' },
];

export function ClientsScreen({ clients, onOpen }: Props) {
  const mobile = useIsMobile();
  const [filter, setFilter] = useState('totes');
  const [search, setSearch] = useState('');

  const list = clients
    .filter(c => {
      const okF = filter === 'totes' || c.status === filter;
      const okS = !search || c.name.toLowerCase().includes(search.toLowerCase());
      return okF && okS;
    })
    .sort((a, b) => a.days_until - b.days_until);

  const px = mobile ? 20 : 40;

  const searchBox = (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, border: `1px solid ${T.hairline}`, padding: '7px 12px', borderRadius: 2, background: T.vellum, minWidth: mobile ? 'auto' : 220 }}>
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke={T.ink3} strokeWidth="1.5">
        <circle cx="5" cy="5" r="3.5"/><path d="M8 8l2.5 2.5" strokeLinecap="round"/>
      </svg>
      <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Cerca…"
        style={{ border: 'none', background: 'none', fontFamily: T.sans, fontSize: 13, color: T.ink, outline: 'none', width: '100%' }} />
    </div>
  );

  const chips = (
    <div style={{ display: 'flex', gap: 6, overflowX: 'auto', scrollbarWidth: 'none' }}>
      {CHIPS.map(f => {
        const on = filter === f.id;
        return (
          <button key={f.id} onClick={() => setFilter(f.id)} style={{
            padding: '4px 12px', flexShrink: 0,
            fontFamily: T.mono, fontSize: 9, letterSpacing: 0.8, textTransform: 'uppercase',
            border: `1px solid ${on ? T.ink : T.hairline}`,
            background: on ? T.ink : 'transparent',
            color: on ? T.paper : T.ink3,
            borderRadius: 2, cursor: 'pointer',
          }}>{f.l}</button>
        );
      })}
    </div>
  );

  if (!mobile) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
        <PageHeader eyebrow="Atelier · Taller" title="Clientes" subtitle={`${clients.length} noives`} right={searchBox} />
        <div style={{ padding: `14px ${px}px 0`, flexShrink: 0 }}>{chips}</div>
        <div style={{ flex: 1, overflow: 'auto', padding: `0 ${px}px 32px` }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 16 }}>
            <thead>
              <tr>
                {['Clienta', 'Peça', 'Estat', 'Boda', 'Dies', 'Teles'].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '8px 12px 8px 0', fontFamily: T.mono, fontSize: 9, letterSpacing: 1, textTransform: 'uppercase', color: T.ink3, borderBottom: `1px solid ${T.hairline}`, fontWeight: 400 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {list.map(c => {
                const past = c.days_until < 0;
                return (
                  <tr key={c.id} onClick={() => onOpen(c.id)} style={{ cursor: 'pointer', borderBottom: `1px solid ${T.hairline}` }}
                    onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = T.paper2; }}
                    onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = 'transparent'; }}>
                    <td style={{ padding: '13px 12px 13px 0' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{ width: 32, height: 32, borderRadius: '50%', background: T.paper3, border: `1px solid ${T.hairline}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T.serif, fontSize: 13, fontStyle: 'italic', color: T.ink2, flexShrink: 0 }}>{initials(c.name)}</div>
                        <span style={{ fontFamily: T.sans, fontSize: 13, color: T.ink, fontWeight: 500 }}>{c.name}</span>
                      </div>
                    </td>
                    <td style={{ padding: '13px 12px 13px 0' }}><Mono size={11} color={T.ink2}>{c.garment || '—'}</Mono></td>
                    <td style={{ padding: '13px 12px 13px 0' }}><Badge status={c.status} size="sm" /></td>
                    <td style={{ padding: '13px 12px 13px 0' }}><Mono size={11}>{c.wedding_date}</Mono></td>
                    <td style={{ padding: '13px 12px 13px 0' }}>
                      <Mono size={11} color={past ? T.accent : T.ink2}>{past ? `−${Math.abs(c.days_until)}d` : `${c.days_until}d`}</Mono>
                    </td>
                    <td style={{ padding: '13px 0' }}>
                      <Mono size={11} color={T.ink3}>{c.fabrics.length > 0 ? String(c.fabrics.length) : '—'}</Mono>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {list.length === 0 && (
            <div style={{ textAlign: 'center', padding: '60px 0', fontFamily: T.serif, fontSize: 22, fontStyle: 'italic', color: T.ink3 }}>Cap resultat</div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <PageHeader eyebrow="Atelier" title="Clientes" subtitle={`${clients.length}`} right={searchBox} />
      <div style={{ padding: '10px 20px 0', flexShrink: 0 }}>{chips}</div>
      <div style={{ flex: 1, overflow: 'auto', padding: '10px 16px 24px' }}>
        {list.map(c => {
          const past = c.days_until < 0;
          return (
            <div key={c.id} onClick={() => onOpen(c.id)} style={{ background: T.vellum, border: `1px solid ${T.hairline}`, borderRadius: 4, padding: '14px', marginBottom: 8, cursor: 'pointer' }}>
              <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 10 }}>
                <div style={{ width: 40, height: 40, borderRadius: '50%', background: T.paper3, border: `1px solid ${T.hairline}`, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T.serif, fontSize: 16, fontStyle: 'italic', color: T.ink2 }}>{initials(c.name)}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: T.sans, fontSize: 14, fontWeight: 500, color: T.ink }}>{c.name}</div>
                  <Mono size={10} color={T.ink3}>{c.garment || '—'}</Mono>
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <Mono size={11}>{c.wedding_date}</Mono>
                  <div style={{ marginTop: 2 }}>
                    <Mono size={9} color={past ? T.accent : T.ink3}>{past ? `−${Math.abs(c.days_until)}d` : `d−${c.days_until}`}</Mono>
                  </div>
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Badge status={c.status} size="sm" />
                {c.fabrics.length > 0 && <Mono size={9} color={T.ink3}>{c.fabrics.length} teles</Mono>}
              </div>
            </div>
          );
        })}
        {list.length === 0 && (
          <div style={{ textAlign: 'center', padding: '48px 0', fontFamily: T.serif, fontSize: 18, fontStyle: 'italic', color: T.ink3 }}>Cap resultat</div>
        )}
      </div>
    </div>
  );
}
