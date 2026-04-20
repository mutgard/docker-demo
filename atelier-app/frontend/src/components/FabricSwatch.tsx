export function FabricSwatch({ size = 32 }: { size?: number }) {
  return (
    <div style={{
      width: size, height: size, flexShrink: 0, borderRadius: 2,
      border: '1px solid var(--line)',
      background: 'repeating-linear-gradient(45deg, var(--line) 0 .8px, var(--bg-card) .8px 5px)',
    }} />
  );
}
