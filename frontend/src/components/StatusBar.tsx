export function StatusBar() {
  return (
    <div style={{
      height: 36, display: 'flex', alignItems: 'center',
      justifyContent: 'space-between', padding: '0 22px', flexShrink: 0,
    }}>
      <span style={{ fontFamily: 'var(--font-m)', fontSize: 12, fontWeight: 500, color: 'var(--ink-1)' }}>9:41</span>
      <div style={{ display: 'flex', gap: 6, alignItems: 'center', color: 'var(--ink-1)' }}>
        <svg width="15" height="10" viewBox="0 0 15 10" fill="currentColor">
          <rect x="0" y="7" width="3" height="3" rx=".4"/>
          <rect x="4" y="5" width="3" height="5" rx=".4"/>
          <rect x="8" y="2.5" width="3" height="7.5" rx=".4"/>
          <rect x="12" y="0" width="3" height="10" rx=".4"/>
        </svg>
        <svg width="18" height="11" viewBox="0 0 18 11" fill="none">
          <rect x=".6" y=".6" width="14" height="9.8" rx="2.2" stroke="currentColor" strokeWidth="1.2"/>
          <rect x="15.2" y="3.5" width="2.2" height="4" rx=".8" fill="currentColor"/>
          <rect x="1.5" y="1.5" width="9.5" height="8" rx="1.5" fill="currentColor"/>
        </svg>
      </div>
    </div>
  );
}
