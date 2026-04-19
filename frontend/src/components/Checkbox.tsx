export function Checkbox({ checked, onChange }: { checked: boolean; onChange: () => void }) {
  return (
    <div onClick={onChange} style={{
      width: 17, height: 17, flexShrink: 0, borderRadius: 2, cursor: 'pointer',
      border: `1.5px solid ${checked ? 'var(--ink-1)' : 'var(--line)'}`,
      background: checked ? 'var(--ink-1)' : 'transparent',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      transition: 'all .15s ease',
    }}>
      {checked && (
        <svg width="9" height="7" viewBox="0 0 9 7" fill="none" stroke="white" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
          <path d="M1 3.5l2.5 2.5 5-5"/>
        </svg>
      )}
    </div>
  );
}
