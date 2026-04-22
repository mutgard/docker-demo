import { useState, useEffect } from 'react';
import type { Client, AtelierEvent } from '../types';
import { api } from '../api';
import { T, fabricVariant } from '../tokens';
import { useIsMobile } from '../hooks/useIsMobile';
import { Label, Mono, Serif, Badge, Swatch, Checkbox } from '../components/primitives';
import { initials, parsePayments } from '../lib/clientHelpers';
import { IntakeTab } from '../components/IntakeTab';
import { EventList } from '../components/EventList';
import { isoToday } from '../lib/calendarHelpers';

interface Props {
  client: Client;
  onBack: () => void;
  onOpenFabrics: () => void;
  onRefresh: () => void;
  allClients: Client[];
}

export function ProfileScreen({ client: initial, onBack, onOpenFabrics, onRefresh, allClients }: Props) {
  const [c, setC] = useState<Client>(initial);
  const mobile = useIsMobile();
  const [tab, setTab] = useState<'fitxa' | 'ingres'>('fitxa');
  const [briefToken, setBriefToken] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [clientEvents, setClientEvents] = useState<AtelierEvent[]>([]);
  const [editing, setEditing] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [draft, setDraft] = useState({
    name: c.name,
    phone: c.phone,
    email: c.email,
    wedding_date: c.wedding_date,
    wedding_date_iso: c.wedding_date_iso ?? '',
    garment: c.garment,
    garment_style: c.garment_style,
    notes: c.notes,
    status: c.status,
  });

  const fetchClientEvents = () => {
    api.listEvents(isoToday(), '9999-12-31', c.id).then(setClientEvents);
  };

  useEffect(() => {
    if (!c) return;
    api.getIntake(c.id)
      .then(data => setBriefToken(data?.token ?? null))
      .catch(() => setBriefToken(null));
  }, [c?.id]);

  useEffect(() => { fetchClientEvents(); }, [c.id]);

  if (!c) return null;

  const past = c.days_until < 0;
  const { priceTotal, paid } = parsePayments(c.payments);
  const pct = priceTotal && priceTotal > 0 ? Math.min(100, Math.round((paid / priceTotal) * 100)) : 0;
  const px = mobile ? 20 : 40;

  const handleCopyLink = async () => {
    if (!briefToken) return;
    try {
      await navigator.clipboard.writeText(`${window.location.origin}/brief/${briefToken}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard not available — silently fail
    }
  };

  const handleToggle = async (fabricId: number, current: boolean) => {
    await api.patchFabric(fabricId, { to_buy: !current });
    const updated = await api.getClient(c.id);
    setC(updated);
    onRefresh();
  };

  const startEdit = () => {
    setDraft({
      name: c.name,
      phone: c.phone,
      email: c.email,
      wedding_date: c.wedding_date,
      wedding_date_iso: c.wedding_date_iso ?? '',
      garment: c.garment,
      garment_style: c.garment_style,
      notes: c.notes,
      status: c.status,
    });
    setEditing(true);
  };

  const cancelEdit = () => setEditing(false);

  const saveEdit = async () => {
    setSaveError('');
    try {
      const days = draft.wedding_date_iso
        ? Math.round((new Date(draft.wedding_date_iso).getTime() - Date.now()) / 86400000)
        : c.days_until;
      const wedding_date = draft.wedding_date_iso
        ? (() => { const [y, m, d] = draft.wedding_date_iso.split('-'); return `${d}.${m}.${y}`; })()
        : c.wedding_date;
      await api.patchClient(c.id, {
        name: draft.name,
        phone: draft.phone,
        email: draft.email,
        wedding_date,
        wedding_date_iso: draft.wedding_date_iso || undefined,
        days_until: days,
        garment: draft.garment,
        garment_style: draft.garment_style,
        notes: draft.notes,
        status: draft.status,
      });
      const updated = await api.getClient(c.id);
      setC(updated);
      onRefresh();
      setEditing(false);
    } catch {
      setSaveError('Error en guardar. Torna-ho a provar.');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Back bar */}
      <div style={{ padding: `10px ${px}px`, borderBottom: `1px solid ${T.hairline}`, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <button onClick={onBack} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: T.mono, fontSize: 10, letterSpacing: 0.8, textTransform: 'uppercase', color: T.ink2, padding: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
          ← Clientes
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {briefToken && (
            <button
              onClick={handleCopyLink}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                fontFamily: T.mono, fontSize: 10, letterSpacing: 0.8,
                textTransform: 'uppercase', padding: 0,
                color: copied ? T.accent : T.ink3,
              }}
            >
              {copied ? 'Copiat ✓' : 'Copiar link'}
            </button>
          )}
          <Label style={{ color: T.ink3 }}>02 · Fitxa</Label>
        </div>
      </div>

      {/* Hero */}
      <div style={{ padding: `${mobile ? 20 : 28}px ${px}px ${mobile ? 18 : 22}px`, borderBottom: `1px solid ${T.hairline}`, background: T.paper, flexShrink: 0, display: 'flex', alignItems: 'flex-start', gap: 20 }}>
        <div style={{ width: mobile ? 52 : 68, height: mobile ? 52 : 68, borderRadius: '50%', background: T.paper3, border: `1px solid ${T.hairline}`, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T.serif, fontStyle: 'italic', fontSize: mobile ? 20 : 26, color: T.ink2 }}>{initials(c.name)}</div>
        <div style={{ flex: 1 }}>
          <Serif size={mobile ? 32 : 40} italic>{c.name}</Serif>
          <div style={{ marginTop: 6, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <Badge status={c.status} />
            {clientEvents.length > 0 && (
              <Mono size={10} color={T.ink3}>
                {clientEvents[0].title} · {clientEvents[0].date}
              </Mono>
            )}
          </div>
          {(c.phone || c.email) && (
            <div style={{ marginTop: 8, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              {c.phone && <Mono size={10} color={T.ink2}>{c.phone}</Mono>}
              {c.email && <Mono size={10} color={T.ink2}>{c.email}</Mono>}
            </div>
          )}
        </div>
      </div>

      {/* Tab strip */}
      <div style={{ display: 'flex', borderBottom: `1px solid ${T.hairline}`, flexShrink: 0, background: T.paper }}>
        {(['fitxa', 'ingres'] as const).map((t) => {
          const labels = { fitxa: 'Fitxa', ingres: 'Ingrés' };
          const on = tab === t;
          return (
            <div
              key={t}
              onClick={() => setTab(t)}
              style={{
                padding: '10px 20px',
                cursor: 'pointer',
                position: 'relative',
                fontFamily: T.serif,
                fontSize: 15,
                fontStyle: on ? 'italic' : 'normal',
                color: on ? T.ink : T.ink3,
              }}
            >
              {labels[t]}
              {on && (
                <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 2, background: T.accent }} />
              )}
            </div>
          );
        })}
      </div>

      {/* Scrollable content */}
      <div style={{ flex: 1, overflow: 'auto', padding: `${mobile ? 20 : 28}px ${px}px 40px`, display: tab === 'fitxa' ? 'block' : 'none' }}>

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

        {/* Esdeveniments */}
        <EventList
          events={clientEvents}
          clients={allClients}
          defaultClientId={c.id}
          onRefresh={fetchClientEvents}
        />

        {/* Notes */}
        {c.notes && (
          <div style={{ marginBottom: 24 }}>
            <Label style={{ marginBottom: 8 }}>Notes</Label>
            <div style={{ fontFamily: T.sans, fontSize: 13, color: T.ink2, lineHeight: 1.65 }}>{c.notes}</div>
          </div>
        )}
      </div>
      {tab === 'ingres' && (
        <div style={{ flex: 1, minHeight: 0, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
          <IntakeTab clientId={c.id} />
        </div>
      )}
    </div>
  );
}
