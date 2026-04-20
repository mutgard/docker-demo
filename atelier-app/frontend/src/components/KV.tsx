export function KV({ k, v }: { k: string; v: string }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
      padding: '7px 0', borderBottom: '1px solid var(--line)',
    }}>
      <span style={{
        fontFamily: 'var(--font-m)', fontSize: 9, letterSpacing: '.8px',
        textTransform: 'uppercase', color: 'var(--ink-3)',
      }}>{k}</span>
      <span style={{ fontFamily: 'var(--font-u)', fontSize: 13, color: 'var(--ink-2)' }}>{v}</span>
    </div>
  );
}
