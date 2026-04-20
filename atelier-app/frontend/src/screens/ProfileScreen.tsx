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
  const soon = !past && c.days_until <= 30;

  const handleToggleBuy = async (fabricId: number, current: boolean) => {
    await api.patchFabric(fabricId, { to_buy: !current });
    const updated = await api.getClient(c.id);
    setC(updated);
  };

  return (
    <div className={animClass} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg-app)' }}>

      {/* Nav bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 20px', flexShrink: 0, borderBottom: '1px solid var(--line)' }}>
        <button onClick={onBack} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: 'none', color: 'var(--accent)', fontFamily: 'var(--font-u)', fontSize: 13, padding: '4px 0' }}>
          <svg width="7" height="12" viewBox="0 0 8 13" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M7 1L1 6.5L7 12"/>
          </svg>
          Clientes
        </button>
        <span style={{ fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '1.5px', textTransform: 'uppercase', color: 'var(--ink-3)' }}>Edita</span>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px 32px' }}>

        {/* Identity */}
        <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start', marginBottom: 20 }}>
          <div style={{
            width: 68, height: 68, borderRadius: '50%', flexShrink: 0,
            border: '1px solid var(--line)',
            background: 'linear-gradient(135deg, var(--bg-card) 0%, var(--line) 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: 'var(--font-d)', fontSize: 28, fontStyle: 'italic', color: 'var(--ink-3)',
          }}>
            {c.name[0]}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: 'var(--font-d)', fontSize: 'clamp(24px, 3vw, 34px)', fontWeight: 300, fontStyle: 'italic', color: 'var(--ink-1)', lineHeight: 1.1, marginBottom: 6 }}>{c.name}</div>
            <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)', lineHeight: 2, letterSpacing: '.3px' }}>
              {c.phone}<br/>{c.email}
            </div>
            <div style={{ marginTop: 10 }}><Badge status={c.status} /></div>
          </div>
        </div>

        {/* Countdown */}
        {c.status !== 'entregada' && (
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '16px 18px', marginBottom: 24,
            background: 'var(--bg-card)', border: '1px solid var(--line)', borderRadius: 4,
          }}>
            <div>
              <div style={{ fontFamily: 'var(--font-m)', fontSize: 7, letterSpacing: '2px', textTransform: 'uppercase', color: 'var(--ink-4)', marginBottom: 5 }}>Boda</div>
              <div style={{ fontFamily: 'var(--font-m)', fontSize: 13, color: 'var(--ink-2)' }}>{c.wedding_date}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontFamily: 'var(--font-m)', fontSize: 7, letterSpacing: '2px', textTransform: 'uppercase', color: 'var(--ink-4)', marginBottom: 4 }}>Compte enrere</div>
              <div style={{
                fontFamily: 'var(--font-d)', fontSize: 'clamp(28px, 3.5vw, 42px)',
                fontStyle: 'italic', fontWeight: 300,
                color: soon ? 'var(--accent)' : 'var(--ink-1)',
              }}>
                {past ? `−${Math.abs(c.days_until)}` : c.days_until} <span style={{ fontSize: '0.55em', fontWeight: 400 }}>dies</span>
              </div>
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
              <div key={f.id} style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '10px 0', borderBottom: i < c.fabrics.length - 1 ? '1px solid var(--line)' : 'none' }}>
                <Checkbox checked={f.to_buy} onChange={() => handleToggleBuy(f.id, f.to_buy)} />
                <FabricSwatch size={28} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: 'var(--font-u)', fontSize: 13, color: 'var(--ink-1)' }}>{f.name}</div>
                  <div style={{ fontFamily: 'var(--font-m)', fontSize: 9, color: 'var(--ink-3)', marginTop: 2, letterSpacing: '.2px' }}>{f.use} · {f.qty} · {f.price}</div>
                </div>
                {f.to_buy && (
                  <span style={{ fontFamily: 'var(--font-m)', fontSize: 7, letterSpacing: '.8px', textTransform: 'uppercase', color: 'var(--accent)', border: '1px solid var(--accent-l)', padding: '2px 5px', borderRadius: 1, flexShrink: 0 }}>Comprar</span>
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
            ? <div style={{ fontFamily: 'var(--font-u)', fontSize: 13, color: 'var(--ink-2)', lineHeight: 1.7 }}>{c.notes}</div>
            : <div style={{ opacity: .2, display: 'flex', flexDirection: 'column', gap: 6, paddingTop: 4 }}>
                {[100, 74, 48].map((w, i) => <div key={i} style={{ height: 6, width: `${w}%`, background: 'var(--ink-3)', borderRadius: 2 }}/>)}
              </div>
          }
        </Section>
      </div>
    </div>
  );
}
