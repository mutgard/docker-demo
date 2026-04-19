import { useState, useEffect } from 'react';
import { api } from '../api';
import type { Client, Fabric } from '../types';
import { Checkbox } from '../components/Checkbox';
import { FabricSwatch } from '../components/FabricSwatch';

interface Props { animClass: string; }

function FabricRow({ fabric: f, onToggle }: { fabric: Fabric; onToggle: (id: number, current: boolean) => void }) {
  return (
    <div style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '10px 4px', borderBottom: '1px dashed var(--line-l)' }}>
      <Checkbox checked={f.to_buy} onChange={() => onToggle(f.id, f.to_buy)} />
      <FabricSwatch size={30} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontFamily: 'var(--font-u)', fontSize: 12, fontWeight: 500, color: 'var(--ink-1)' }}>{f.name}</div>
        <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)', marginTop: 1 }}>{f.use} · {f.qty} · {f.price}</div>
      </div>
      {f.to_buy && (
        <span style={{ fontFamily: 'var(--font-m)', fontSize: 7, textTransform: 'uppercase', letterSpacing: '.5px', color: 'var(--accent)', border: '1px solid var(--accent)', padding: '1px 4px', borderRadius: 1, flexShrink: 0 }}>Comprar</span>
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

  // aggregate by fabric name
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
      <div style={{ padding: '10px 20px 0', flexShrink: 0 }}>
        <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--ink-3)', marginBottom: 1 }}>Inventari</div>
        <div style={{ fontFamily: 'var(--font-d)', fontSize: 34, fontWeight: 400, color: 'var(--ink-1)', letterSpacing: '-.3px', lineHeight: 1.1, marginBottom: 14 }}>Teles</div>
        <div style={{ display: 'flex', border: '1px solid var(--line)', borderRadius: 6, overflow: 'hidden', marginBottom: 4 }}>
          {([{ id: 'client', l: 'Per clienta' }, { id: 'fabric', l: 'Per tela' }] as const).map((o, i) => (
            <button key={o.id} onClick={() => setGroupBy(o.id)} style={{
              flex: 1, padding: '8px 0', fontFamily: 'var(--font-m)', fontSize: 9, letterSpacing: '.5px', textTransform: 'uppercase',
              border: 'none', borderRight: i === 0 ? '1px solid var(--line)' : 'none',
              background: groupBy === o.id ? 'var(--ink-1)' : 'var(--bg-card)',
              color: groupBy === o.id ? 'var(--bg-card)' : 'var(--ink-3)',
              transition: 'all .18s ease',
            }}>
              {o.l}
            </button>
          ))}
        </div>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '6px 14px 24px' }}>
        {groupBy === 'client'
          ? clients.map(c => (
            <div key={c.id} style={{ marginTop: 14 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '7px 4px', borderBottom: '1.5px solid var(--ink-1)' }}>
                <span style={{ fontFamily: 'var(--font-u)', fontSize: 13, fontWeight: 600, color: 'var(--ink-1)' }}>{c.name}</span>
                <span style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)' }}>Boda · {c.wedding_date.split(' ').slice(0, 2).join(' ')}</span>
              </div>
              {c.fabrics.map(f => <FabricRow key={f.id} fabric={f} onToggle={handleToggle} />)}
            </div>
          ))
          : aggList.map((f, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '12px 4px', borderBottom: '1px dashed var(--line)' }}>
              <Checkbox checked={f.to_buy} onChange={() => {}} />
              <FabricSwatch size={36} />
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: 'var(--font-u)', fontSize: 13, fontWeight: 500, color: 'var(--ink-1)' }}>{f.name}</div>
                <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)', marginTop: 1 }}>{f.qty.toFixed(1)} m total · {f.price}</div>
                <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-4)', marginTop: 1 }}>{f.clients.join(' · ')}</div>
              </div>
            </div>
          ))
        }
      </div>
    </div>
  );
}
