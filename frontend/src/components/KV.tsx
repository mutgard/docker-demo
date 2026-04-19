export function KV({ k, v }: { k: string; v: string }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
      padding: '5px 0', borderBottom: '1px solid var(--line-l)',
    }}>
      <span style={{
        fontFamily: 'var(--font-m)', fontSize: 9, letterSpacing: '.5px',
        textTransform: 'uppercase', color: 'var(--ink-3)',
      }}>{k}</span>
      <span style={{ fontFamily: 'var(--font-u)', fontSize: 13, color: 'var(--ink-1)' }}>{v}</span>
    </div>
  );
}
