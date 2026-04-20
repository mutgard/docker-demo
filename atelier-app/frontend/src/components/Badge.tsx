import type { ClientStatus } from '../types';

const STATUS = {
  'prospect':   { label: 'Prospect',           glyph: '◌', border: '1px dashed var(--ink-4)', bg: 'transparent',               fg: 'var(--ink-3)' },
  'sense-paga': { label: 'Sense paga i senyal', glyph: '◑', border: '1px solid var(--accent-l)', bg: 'rgba(184,134,90,.10)',    fg: 'var(--accent)' },
  'clienta':    { label: 'Clienta',             glyph: '●', border: '1px solid var(--ink-2)',  bg: 'var(--ink-1)',              fg: 'var(--bg-app)' },
  'entregada':  { label: 'Entregada',           glyph: '✓', border: '1px solid var(--line)',   bg: 'transparent',              fg: 'var(--ink-3)' },
};

export function Badge({ status }: { status: ClientStatus }) {
  const s = STATUS[status];
  if (!s) return null;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      padding: '2px 7px', border: s.border, background: s.bg, color: s.fg,
      fontFamily: 'var(--font-m)', fontSize: 8, letterSpacing: '.6px',
      textTransform: 'uppercase', borderRadius: 1, flexShrink: 0, lineHeight: 1.7,
    }}>
      <span style={{ fontSize: 9 }}>{s.glyph}</span>{s.label}
    </span>
  );
}
