import { useState, useEffect } from 'react';
import { api } from '../api';
import type { Client, Fabric } from '../types';
import { Checkbox } from '../components/Checkbox';
import { FabricSwatch } from '../components/FabricSwatch';

interface Props { animClass: string; }

function FabricRow({ fabric: f, onToggle }: { fabric: Fabric; onToggle: (id: number, current: boolean) => void }) {
  return (
    <div style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '10px 0', borderBottom: '1px solid var(--line)' }}>
      <Checkbox checked={f.to_buy} onChange={() => onToggle(f.id, f.to_buy)} />
      <FabricSwatch size={30} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontFamily: 'var(--font-u)', fontSize: 13, color: 'var(--ink-1)' }}>{f.name}</div>
        <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)', marginTop: 2, letterSpacing: '.2px' }}>{f.use} · {f.qty} · {f.price}</div>
      </div>
      {f.to_buy && (
        <span style={{ fontFamily: 'var(--font-m)', fontSize: 7, textTransform: 'uppercase', letterSpacing: '.8px', color: 'var(--accent)', border: '1px solid var(--accent-l)', padding: '2px 5px', borderRadius: 1, flexShrink: 0 }}>Comprar</span>
      )}
    </div>
  );
}

export function FabricsScreen({ animClass }: Props) {
  const [clients, setClients] = useState<Client[]>([]);
  const [groupBy, setGroupBy] = useState<'client' | 'fabric'>('client');

  const load = () => {
    api.listClients().then(cs =>
      setClients(cs.filter(c => c.fabrics.length > 0).sort((a, b) => a.days_until - b.days_until))
    );
  };
  useEffect(load, []);

  const handleToggle = async (fabricId: number, current: boolean) => {
    await api.patchFabric(fabricId, { to_buy: !current });
    load();
  };

  const agg: Record<string, { name: string; price: string; qty: number; clients: string[]; to_buy: boolean }> = {};
  clients.forEach(c => c.fabrics.forEach(f => {
    if (!agg[f.name]) agg[f.name] = { name: f.name, price: f.price, qty: 0, clients: [], to_buy: false };
    agg[f.name].qty += parseFloat(f.qty);
    agg[f.name].clients.push(c.name.split(' ')[0]);
    agg[f.name].to_buy = agg[f.name].to_buy || f.to_buy;
  }));
  const aggList = Object.values(agg);

  return (
    <div className={animClass} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg-app)' }}>

      {/* Header */}
      <div style={{ padding: '20px 24px 0', flexShrink: 0 }}>
        <div style={{ fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '2.5px', textTransform: 'uppercase', color: 'var(--ink-4)', marginBottom: 4 }}>Inventari</div>
        <div style={{ fontFamily: 'var(--font-d)', fontSize: 'clamp(34px, 4vw, 48px)', fontWeight: 300, fontStyle: 'italic', color: 'var(--ink-1)', lineHeight: 1, marginBottom: 18 }}>Teles</div>

        {/* Toggle */}
        <div style={{ display: 'flex', border: '1px solid var(--line)', borderRadius: 3, overflow: 'hidden', marginBottom: 4, maxWidth: 280 }}>
          {([{ id: 'client', l: 'Per clienta' }, { id: 'fabric', l: 'Per tela' }] as const).map((o, i) => (
            <button key={o.id} onClick={() => setGroupBy(o.id)} style={{
              flex: 1, padding: '8px 0',
              fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '1px', textTransform: 'uppercase',
              border: 'none', borderRight: i === 0 ? '1px solid var(--line)' : 'none',
              background: groupBy === o.id ? 'var(--ink-1)' : 'var(--bg-card)',
              color: groupBy === o.id ? 'var(--bg-app)' : 'var(--ink-3)',
              transition: 'all .18s ease',
            }}>
              {o.l}
            </button>
          ))}
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '10px 24px 24px' }}>
        {groupBy === 'client'
          ? clients.map(c => (
            <div key={c.id} style={{ marginTop: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '8px 0', borderBottom: '1px solid var(--ink-2)' }}>
                <span style={{ fontFamily: 'var(--font-d)', fontSize: 16, fontStyle: 'italic', fontWeight: 400, color: 'var(--ink-1)' }}>{c.name}</span>
                <span style={{ fontFamily: 'var(--font-m)', fontSize: 8, color: 'var(--ink-4)', letterSpacing: '.5px' }}>Boda · {c.wedding_date.split(' ').slice(0, 2).join(' ')}</span>
              </div>
              {c.fabrics.map(f => <FabricRow key={f.id} fabric={f} onToggle={handleToggle} />)}
            </div>
          ))
          : aggList.map((f, i) => (
            <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'center', padding: '13px 0', borderBottom: '1px solid var(--line)' }}>
              <Checkbox checked={f.to_buy} onChange={() => {}} />
              <FabricSwatch size={34} />
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: 'var(--font-u)', fontSize: 13, color: 'var(--ink-1)' }}>{f.name}</div>
                <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)', marginTop: 2 }}>{f.qty.toFixed(1)} m total · {f.price}</div>
                <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-4)', marginTop: 2 }}>{f.clients.join(' · ')}</div>
              </div>
            </div>
          ))
        }
      </div>
    </div>
  );
}
