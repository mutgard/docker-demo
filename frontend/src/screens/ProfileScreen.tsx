import { useState } from 'react';
import type { Client } from '../types';
import { api } from '../api';
import { Badge } from '../components/Badge';
import { Checkbox } from '../components/Checkbox';
import { FabricSwatch } from '../components/FabricSwatch';
import { KV } from '../components/KV';
import { Section } from '../components/Section';

interface Props { client: Client; onBack: () => void; animClass: string; }

export function ProfileScreen({ client: initial, onBack, animClass }: Props) {
  const [c, setC] = useState<Client>(initial);
  const past = c.days_until < 0;

  const handleToggleBuy = async (fabricId: number, current: boolean) => {
    await api.patchFabric(fabricId, { to_buy: !current });
    const updated = await api.getClient(c.id);
    setC(updated);
  };

  return (
    <div className={animClass} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg-app)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 16px', flexShrink: 0 }}>
        <button onClick={onBack} style={{ display: 'flex', alignItems: 'center', gap: 5, background: 'none', border: 'none', color: 'var(--accent)', fontFamily: 'var(--font-u)', fontSize: 13, padding: '4px 0' }}>
          <svg width="8" height="13" viewBox="0 0 8 13" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M7 1L1 6.5L7 12"/></svg>
          Clientes
        </button>
        <span style={{ fontFamily: 'var(--font-m)', fontSize: 9, letterSpacing: '.5px', textTransform: 'uppercase', color: 'var(--ink-3)' }}>Edita</span>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '6px 20px 24px' }}>
        <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start', marginBottom: 16 }}>
          <div style={{
            width: 72, height: 72, borderRadius: '50%', flexShrink: 0, border: '1px solid var(--line)',
            background: 'linear-gradient(135deg,var(--line) 0%,var(--line-l) 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'var(--font-d)', fontSize: 28, fontStyle: 'italic', color: 'var(--ink-3)',
          }}>
            {c.name[0]}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: 'var(--font-d)', fontSize: 26, color: 'var(--ink-1)', letterSpacing: '-.3px', lineHeight: 1.1 }}>{c.name}</div>
            <div style={{ fontFamily: 'var(--font-m)', fontSize: 10, color: 'var(--ink-3)', marginTop: 4, lineHeight: 1.9 }}>
              {c.phone}<br/>{c.email}
            </div>
            <div style={{ marginTop: 8 }}><Badge status={c.status} /></div>
          </div>
        </div>
        {c.status !== 'entregada' && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '13px 15px', marginBottom: 20, background: 'var(--bg-card)', border: '1px solid var(--line)', borderRadius: 6 }}>
            <div>
              <div style={{ fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--ink-3)', marginBottom: 3 }}>Boda</div>
              <div style={{ fontFamily: 'var(--font-m)', fontSize: 14, color: 'var(--ink-1)', fontWeight: 500 }}>{c.wedding_date}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--ink-3)', marginBottom: 3 }}>Compte enrere</div>
              <div style={{ fontFamily: 'var(--font-d)', fontSize: 28, color: 'var(--ink-1)', fontStyle: 'italic' }}>{past ? `−${Math.abs(c.days_until)}` : c.days_until} dies</div>
            </div>
          </div>
        )}
        <Section title="Peça">
          <KV k="Tipus" v={c.garment || '—'} />
          <KV k="Estil" v={c.garment_style || '—'} />
          <KV k="Mides" v={c.measurements_date || '—'} />
        </Section>
        {c.fabrics.length > 0 && (
          <Section title={`Teles (${c.fabrics.length})`} action="Veure totes →">
            {c.fabrics.map((f, i) => (
              <div key={f.id} style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '9px 0', borderBottom: i < c.fabrics.length - 1 ? '1px dashed var(--line-l)' : 'none' }}>
                <Checkbox checked={f.to_buy} onChange={() => handleToggleBuy(f.id, f.to_buy)} />
                <FabricSwatch size={28} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: 'var(--font-u)', fontSize: 12, fontWeight: 500, color: 'var(--ink-1)' }}>{f.name}</div>
                  <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)', marginTop: 1 }}>{f.use} · {f.qty} · {f.price}</div>
                </div>
                {f.to_buy && (
                  <span style={{ fontFamily: 'var(--font-m)', fontSize: 7, letterSpacing: '.5px', textTransform: 'uppercase', color: 'var(--accent)', border: '1px solid var(--accent)', padding: '1px 4px', borderRadius: 1, flexShrink: 0 }}>Comprar</span>
                )}
              </div>
            ))}
          </Section>
        )}
        {c.appointments.length > 0 && (
          <Section title="Cites" action="+ Afegir">
            {c.appointments.map((a, i) => <KV key={i} k={a.label} v={a.value} />)}
          </Section>
        )}
        {c.payments.length > 0 && (
          <Section title="Pagaments">
            {c.payments.map((p, i) => <KV key={i} k={p.label} v={p.value} />)}
          </Section>
        )}
        <Section title="Notes">
          {c.notes
            ? <div style={{ fontFamily: 'var(--font-u)', fontSize: 13, color: 'var(--ink-2)', lineHeight: 1.65 }}>{c.notes}</div>
            : <div style={{ opacity: .25, display: 'flex', flexDirection: 'column', gap: 5 }}>
                {[100, 78, 52].map((w, i) => <div key={i} style={{ height: 7, width: `${w}%`, background: 'var(--ink-3)', borderRadius: 2 }}/>)}
              </div>
          }
        </Section>
      </div>
    </div>
  );
}
