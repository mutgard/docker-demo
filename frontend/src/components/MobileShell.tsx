import { T } from '../tokens';

type Screen = 'clients' | 'profile' | 'fabrics' | 'shop';

export function MobileTopBar() {
  return (
    <div style={{
      background: T.ink, color: T.paper,
      padding: '14px 20px 12px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      flexShrink: 0,
    }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
        <span style={{ fontFamily: T.serif, fontSize: 22, color: T.paper, lineHeight: 1 }}>Juliette</span>
        <span style={{ fontFamily: T.serif, fontSize: 22, fontStyle: 'italic', color: T.gold, lineHeight: 1 }}>Atelier</span>
      </div>
      <div style={{
        width: 32, height: 32, borderRadius: '50%', background: T.gold,
        color: T.ink, display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: T.serif, fontSize: 15, fontStyle: 'italic',
      }}>J</div>
    </div>
  );
}

export function MobileTabBar({ active, onNav, fabricsToBuy }: {
  active: Screen;
  onNav: (s: Screen) => void;
  fabricsToBuy: number;
}) {
  const tabs: { id: Screen; n: string; label: string; count?: number }[] = [
    { id: 'clients', n: '01', label: 'Clientes' },
    { id: 'fabrics', n: '03', label: 'Teles' },
    { id: 'shop',    n: '04', label: 'Comprar', count: fabricsToBuy },
  ];

  return (
    <div style={{
      flexShrink: 0, background: T.ink, color: T.paper,
      display: 'flex', padding: '6px 0 20px',
      borderTop: `1px solid rgba(246,241,232,0.15)`,
    }}>
      {tabs.map(t => {
        const on = t.id === active || (active === 'profile' && t.id === 'clients');
        return (
          <div key={t.id} onClick={() => onNav(t.id)} style={{
            flex: 1, textAlign: 'center', padding: '10px 4px', cursor: 'pointer', position: 'relative',
          }}>
            {on && <div style={{ position: 'absolute', left: '30%', right: '30%', top: 0, height: 2, background: T.gold }} />}
            <div style={{ fontFamily: T.mono, fontSize: 9, letterSpacing: 0.8, color: on ? T.gold : 'rgba(246,241,232,0.45)', marginBottom: 4 }}>{t.n}</div>
            <div style={{
              fontFamily: T.serif, fontSize: 16,
              color: on ? T.paper : 'rgba(246,241,232,0.7)',
              fontStyle: on ? 'italic' : 'normal',
              position: 'relative', display: 'inline-block',
            }}>
              {t.label}
              {t.count !== undefined && t.count > 0 && (
                <span style={{
                  position: 'absolute', top: -4, right: -14,
                  background: T.gold, color: T.ink,
                  fontFamily: T.mono, fontSize: 8,
                  padding: '1px 5px', borderRadius: 999, lineHeight: 1.3,
                }}>{t.count}</span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
