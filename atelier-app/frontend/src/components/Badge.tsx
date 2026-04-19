import type { ClientStatus } from '../types';

const STATUS = {
  'prospect':   { label: 'Prospect',           glyph: '◌', border: '1px dashed #1A1612', bg: 'transparent', fg: '#1A1612' },
  'sense-paga': { label: 'Sense paga i senyal', glyph: '◑', border: '1px solid #8B6247',  bg: '#F5EDE6',     fg: '#5C3B25' },
  'clienta':    { label: 'Clienta',             glyph: '●', border: '1px solid #1A1612',  bg: '#1A1612',     fg: '#FDFAF5' },
  'entregada':  { label: 'Entregada',           glyph: '✓', border: '1px solid #C2B9B0',  bg: '#EDE8DF',     fg: '#6B6158' },
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
