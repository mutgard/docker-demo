import { useState, useEffect } from 'react';
import { api } from '../api';
import type { Fabric } from '../types';
import { FabricSwatch } from '../components/FabricSwatch';

interface Props { animClass: string; }

type ShoppingItem = Fabric & { client_name: string };

export function ShoppingScreen({ animClass }: Props) {
  const [items, setItems] = useState<ShoppingItem[]>([]);

  useEffect(() => { api.getShopping().then(setItems); }, []);

  const bySup: Record<string, ShoppingItem[]> = {};
  items.forEach(f => (bySup[f.supplier || 'Sense proveïdor'] ||= []).push(f));

  const metres = items.reduce((s, f) => s + parseFloat(f.qty), 0);
  const eur = items.reduce((s, f) => s + parseFloat(f.price.replace('€', '').replace('/m', '')) * parseFloat(f.qty), 0);

  return (
    <div className={animClass} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg-app)' }}>
      <div style={{ padding: '10px 20px 0', flexShrink: 0 }}>
        <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--ink-3)', marginBottom: 1 }}>Llista de compra</div>
        <div style={{ fontFamily: 'var(--font-d)', fontSize: 34, fontWeight: 400, color: 'var(--ink-1)', letterSpacing: '-.3px', lineHeight: 1.1, marginBottom: 14 }}>Per comprar</div>
        <div style={{ display: 'flex', background: 'var(--bg-card)', border: '1px solid var(--line)', borderRadius: 6, overflow: 'hidden', marginBottom: 4 }}>
          {[{ l: 'Peces', v: String(items.length) }, { l: 'Metres', v: `${metres.toFixed(1)} m` }, { l: 'Total est.', v: `€${Math.round(eur)}` }].map((x, i) => (
            <div key={i} style={{ flex: 1, padding: '12px 10px', borderRight: i < 2 ? '1px solid var(--line-l)' : 'none' }}>
              <div style={{ fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '.8px', textTransform: 'uppercase', color: 'var(--ink-3)', marginBottom: 4 }}>{x.l}</div>
              <div style={{ fontFamily: 'var(--font-d)', fontSize: 22, color: 'var(--ink-1)' }}>{x.v}</div>
            </div>
          ))}
        </div>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '6px 14px 16px' }}>
        {items.length === 0
          ? <div style={{ textAlign: 'center', padding: '48px 0', fontFamily: 'var(--font-d)', fontSize: 18, fontStyle: 'italic', color: 'var(--ink-3)' }}>Cap tela per comprar</div>
          : Object.entries(bySup).map(([sup, fs]) => (
            <div key={sup} style={{ marginTop: 14 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '7px 4px', borderBottom: '1.5px solid var(--ink-1)' }}>
                <span style={{ fontFamily: 'var(--font-u)', fontSize: 13, fontWeight: 600, color: 'var(--ink-1)' }}>{sup}</span>
                <span style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)' }}>{fs.length} peça{fs.length > 1 ? 's' : ''}</span>
              </div>
              {fs.map((f, i) => (
                <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '10px 4px', borderBottom: '1px dashed var(--line-l)' }}>
                  <div style={{ width: 17, height: 17, border: '1.5px solid var(--line)', borderRadius: 2, flexShrink: 0 }}/>
                  <FabricSwatch size={30} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontFamily: 'var(--font-u)', fontSize: 12, fontWeight: 500, color: 'var(--ink-1)' }}>{f.name}</div>
                    <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)', marginTop: 1 }}>{f.qty} · {f.price}</div>
                    <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-4)', marginTop: 1 }}>per {f.client_name.split(' ')[0]}</div>
                  </div>
                  <span style={{ fontFamily: 'var(--font-m)', fontSize: 13, color: 'var(--ink-4)', alignSelf: 'flex-start', paddingTop: 2 }}>⋯</span>
                </div>
              ))}
            </div>
          ))
        }
        {items.length > 0 && (
          <div style={{ marginTop: 20, display: 'flex', gap: 8 }}>
            <button style={{ flex: 1, padding: '12px 0', background: 'var(--ink-1)', color: 'var(--bg-card)', border: 'none', borderRadius: 6, fontFamily: 'var(--font-m)', fontSize: 9, letterSpacing: '.8px', textTransform: 'uppercase' }}>Marcar com demanades</button>
            <button style={{ padding: '12px 14px', background: 'transparent', color: 'var(--ink-2)', border: '1px solid var(--line)', borderRadius: 6, fontFamily: 'var(--font-m)', fontSize: 9 }}>⬡</button>
          </div>
        )}
      </div>
    </div>
  );
}
