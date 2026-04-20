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

      {/* Header */}
      <div style={{ padding: '20px 24px 0', flexShrink: 0 }}>
        <div style={{ fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '2.5px', textTransform: 'uppercase', color: 'var(--ink-4)', marginBottom: 4 }}>Llista de compra</div>
        <div style={{ fontFamily: 'var(--font-d)', fontSize: 'clamp(34px, 4vw, 48px)', fontWeight: 300, fontStyle: 'italic', color: 'var(--ink-1)', lineHeight: 1, marginBottom: 18 }}>Per comprar</div>

        {/* Stats */}
        <div style={{ display: 'flex', background: 'var(--bg-card)', border: '1px solid var(--line)', borderRadius: 4, overflow: 'hidden', marginBottom: 4 }}>
          {[
            { l: 'Peces', v: String(items.length) },
            { l: 'Metres', v: `${metres.toFixed(1)} m` },
            { l: 'Total est.', v: `€${Math.round(eur)}` },
          ].map((x, i) => (
            <div key={i} style={{ flex: 1, padding: '13px 14px', borderRight: i < 2 ? '1px solid var(--line)' : 'none' }}>
              <div style={{ fontFamily: 'var(--font-m)', fontSize: 7, letterSpacing: '1.5px', textTransform: 'uppercase', color: 'var(--ink-4)', marginBottom: 6 }}>{x.l}</div>
              <div style={{ fontFamily: 'var(--font-d)', fontSize: 'clamp(20px, 2.5vw, 28px)', fontWeight: 300, color: 'var(--ink-1)' }}>{x.v}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '10px 24px 20px' }}>
        {items.length === 0
          ? <div style={{ textAlign: 'center', padding: '64px 0', fontFamily: 'var(--font-d)', fontSize: 20, fontStyle: 'italic', color: 'var(--ink-4)' }}>Cap tela per comprar</div>
          : Object.entries(bySup).map(([sup, fs]) => (
            <div key={sup} style={{ marginTop: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '8px 0', borderBottom: '1px solid var(--ink-2)' }}>
                <span style={{ fontFamily: 'var(--font-d)', fontSize: 16, fontStyle: 'italic', fontWeight: 400, color: 'var(--ink-1)' }}>{sup}</span>
                <span style={{ fontFamily: 'var(--font-m)', fontSize: 8, color: 'var(--ink-4)', letterSpacing: '.5px' }}>{fs.length} peça{fs.length > 1 ? 's' : ''}</span>
              </div>
              {fs.map((f, i) => (
                <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '11px 0', borderBottom: '1px solid var(--line)' }}>
                  <div style={{ width: 17, height: 17, border: '1.5px solid var(--line)', borderRadius: 2, flexShrink: 0 }}/>
                  <FabricSwatch size={30} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontFamily: 'var(--font-u)', fontSize: 13, color: 'var(--ink-1)' }}>{f.name}</div>
                    <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)', marginTop: 2 }}>{f.qty} · {f.price}</div>
                    <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-4)', marginTop: 1 }}>per {f.client_name.split(' ')[0]}</div>
                  </div>
                  <span style={{ fontFamily: 'var(--font-m)', fontSize: 13, color: 'var(--ink-4)', alignSelf: 'flex-start', paddingTop: 2 }}>⋯</span>
                </div>
              ))}
            </div>
          ))
        }

        {items.length > 0 && (
          <div style={{ marginTop: 24, display: 'flex', gap: 8 }}>
            <button style={{
              flex: 1, padding: '13px 0',
              background: 'var(--accent)', color: 'var(--bg-app)',
              border: 'none', borderRadius: 3,
              fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '1.5px', textTransform: 'uppercase',
              transition: 'opacity .15s ease',
            }}>Marcar com demanades</button>
            <button style={{
              padding: '13px 16px',
              background: 'transparent', color: 'var(--ink-3)',
              border: '1px solid var(--line)', borderRadius: 3,
              fontFamily: 'var(--font-m)', fontSize: 11,
            }}>⬡</button>
          </div>
        )}
      </div>
    </div>
  );
}
