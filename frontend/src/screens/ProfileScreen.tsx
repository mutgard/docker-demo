import { useState } from 'react';
import type { Client } from '../types';
import { api } from '../api';
import { T, fabricVariant } from '../tokens';
import { useIsMobile } from '../hooks/useIsMobile';
import { Label, Mono, Serif, Badge, Swatch, Checkbox } from '../components/primitives';
import { initials, parsePayments, getNextFitting } from '../lib/clientHelpers';

interface Props {
  client: Client;
  onBack: () => void;
  onOpenFabrics: () => void;
  onRefresh: () => void;
}

export function ProfileScreen({ client: initial, onBack, onOpenFabrics, onRefresh }: Props) {
  const [c, setC] = useState<Client>(initial);
  const mobile = useIsMobile();

  if (!c) return null;

  const past = c.days_until < 0;
  const { priceTotal, paid } = parsePayments(c.payments);
  const pct = priceTotal && priceTotal > 0 ? Math.min(100, Math.round((paid / priceTotal) * 100)) : 0;
  const nextFitting = getNextFitting(c.appointments);
  const px = mobile ? 20 : 40;

  const handleToggle = async (fabricId: number, current: boolean) => {
    await api.patchFabric(fabricId, { to_buy: !current });
    const updated = await api.getClient(c.id);
    setC(updated);
    onRefresh();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Back bar */}
      <div style={{ padding: `10px ${px}px`, borderBottom: `1px solid ${T.hairline}`, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <button onClick={onBack} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: T.mono, fontSize: 10, letterSpacing: 0.8, textTransform: 'uppercase', color: T.ink2, padding: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
          ← Clientes
        </button>
        <Label style={{ color: T.ink3 }}>02 · Fitxa</Label>
      </div>

      {/* Hero */}
      <div style={{ padding: `${mobile ? 20 : 28}px ${px}px ${mobile ? 18 : 22}px`, borderBottom: `1px solid ${T.hairline}`, background: T.paper, flexShrink: 0, display: 'flex', alignItems: 'flex-start', gap: 20 }}>
        <div style={{ width: mobile ? 52 : 68, height: mobile ? 52 : 68, borderRadius: '50%', background: T.paper3, border: `1px solid ${T.hairline}`, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T.serif, fontStyle: 'italic', fontSize: mobile ? 20 : 26, color: T.ink2 }}>{initials(c.name)}</div>
        <div style={{ flex: 1 }}>
          <Serif size={mobile ? 32 : 40} italic>{c.name}</Serif>
          <div style={{ marginTop: 6, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <Badge status={c.status} />
            {nextFitting && <Mono size={10} color={T.ink3}>{nextFitting}</Mono>}
          </div>
          {(c.phone || c.email) && (
            <div style={{ marginTop: 8, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              {c.phone && <Mono size={10} color={T.ink2}>{c.phone}</Mono>}
              {c.email && <Mono size={10} color={T.ink2}>{c.email}</Mono>}
            </div>
          )}
        </div>
      </div>

      {/* Scrollable content */}
      <div style={{ flex: 1, overflow: 'auto', padding: `${mobile ? 20 : 28}px ${px}px 40px` }}>

        {/* Countdown card */}
        {c.status !== 'entregada' && (
          <div style={{ background: T.ink, color: T.paper, padding: '18px 22px', marginBottom: 24 }}>
            <Label style={{ color: 'rgba(246,241,232,0.55)', marginBottom: 8 }}>Compte enrere · Boda</Label>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
                <Serif size={52} italic style={{ color: T.paper }}>{past ? `−${Math.abs(c.days_until)}` : c.days_until}</Serif>
                <Mono size={11} color="rgba(246,241,232,0.55)">dies</Mono>
              </div>
              <div style={{ textAlign: 'right' }}>
                <Mono size={10} color="rgba(246,241,232,0.55)">Data</Mono>
                <div style={{ fontFamily: T.mono, fontSize: 13, color: T.gold, marginTop: 2 }}>{c.wedding_date}</div>
              </div>
            </div>
          </div>
        )}

        {/* Payment progress */}
        {priceTotal !== null && (
          <div style={{ marginBottom: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <Label>Pagaments</Label>
              <Mono size={10}>{paid > 0 ? `€${paid.toLocaleString()}` : '—'} / {priceTotal > 0 ? `€${priceTotal.toLocaleString()}` : '—'}</Mono>
            </div>
            <div style={{ height: 4, background: T.hairline, borderRadius: 2 }}>
              <div style={{ height: '100%', width: `${pct}%`, background: pct >= 100 ? T.accent : T.gold, borderRadius: 2 }} />
            </div>
            <div style={{ marginTop: 8 }}>
              {c.payments.map((p, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: i < c.payments.length - 1 ? `1px solid ${T.hairline}` : 'none' }}>
                  <Mono size={10} color={T.ink3}>{p.label}</Mono>
                  <Mono size={10} color={T.ink}>{p.value}</Mono>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Peça */}
        <div style={{ marginBottom: 24 }}>
          <Label style={{ marginBottom: 10 }}>Peça</Label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            {([['Tipus', c.garment], ['Estil', c.garment_style], ['Data mides', c.measurements_date]] as [string, string][]).map(([k, v]) => v ? (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: `1px solid ${T.hairline}` }}>
                <Mono size={10} color={T.ink3}>{k}</Mono>
                <Mono size={10} color={T.ink}>{v}</Mono>
              </div>
            ) : null)}
          </div>
        </div>

        {/* Teles */}
        {c.fabrics.length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 10 }}>
              <Label>Teles ({c.fabrics.length})</Label>
              <button onClick={onOpenFabrics} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: T.mono, fontSize: 9, letterSpacing: 0.8, textTransform: 'uppercase', color: T.ink3, padding: 0 }}>Veure totes →</button>
            </div>
            {c.fabrics.map((f, i) => (
              <div key={f.id} style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '10px 0', borderBottom: i < c.fabrics.length - 1 ? `1px dashed ${T.hairline}` : 'none' }}>
                <Checkbox checked={f.to_buy} onChange={() => handleToggle(f.id, f.to_buy)} />
                <Swatch size={32} variant={fabricVariant(f.name)} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: T.sans, fontSize: 12, fontWeight: 500, color: T.ink }}>{f.name}</div>
                  <Mono size={9} color={T.ink3}>{f.use} · {f.qty} · {f.price}</Mono>
                </div>
                {f.to_buy && <span style={{ fontFamily: T.mono, fontSize: 8, letterSpacing: 0.5, textTransform: 'uppercase', color: T.accent, border: `1px solid ${T.accent}`, padding: '2px 5px', flexShrink: 0 }}>Comprar</span>}
              </div>
            ))}
          </div>
        )}

        {/* Cites */}
        {c.appointments.length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <Label style={{ marginBottom: 10 }}>Cites</Label>
            {c.appointments.map((a, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: `1px solid ${T.hairline}` }}>
                <Mono size={11} color={T.ink2}>{a.label}</Mono>
                <Mono size={11} color={T.ink}>{a.value}</Mono>
              </div>
            ))}
          </div>
        )}

        {/* Notes */}
        {c.notes && (
          <div style={{ marginBottom: 24 }}>
            <Label style={{ marginBottom: 8 }}>Notes</Label>
            <div style={{ fontFamily: T.sans, fontSize: 13, color: T.ink2, lineHeight: 1.65 }}>{c.notes}</div>
          </div>
        )}
      </div>
    </div>
  );
}
