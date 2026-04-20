import { T } from '../tokens';

type Screen = 'clients' | 'profile' | 'fabrics' | 'shop';

/**
 * Single compact header: brand row + tab strip.
 * Lives at the top so it's always visible regardless of browser chrome.
 */
export function MobileHeader({ active, onNav, fabricsToBuy }: {
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
    <div style={{ background: T.ink, color: T.paper, flexShrink: 0 }}>
      {/* Brand row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 20px 8px' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
          <span style={{ fontFamily: T.serif, fontSize: 20, color: T.paper, lineHeight: 1 }}>Juliette</span>
          <span style={{ fontFamily: T.serif, fontSize: 20, fontStyle: 'italic', color: T.gold, lineHeight: 1 }}>Atelier</span>
        </div>
        <div style={{ width: 28, height: 28, borderRadius: '50%', background: T.gold, color: T.ink, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T.serif, fontSize: 13, fontStyle: 'italic' }}>J</div>
      </div>

      {/* Tab strip — indicator at bottom edge, pointing into content */}
      <div style={{ display: 'flex', borderTop: `1px solid rgba(246,241,232,0.12)` }}>
        {tabs.map(t => {
          const on = t.id === active || (active === 'profile' && t.id === 'clients');
          return (
            <div key={t.id} onClick={() => onNav(t.id)} style={{ flex: 1, textAlign: 'center', padding: '8px 4px 10px', cursor: 'pointer', position: 'relative' }}>
              <div style={{ fontFamily: T.mono, fontSize: 8, letterSpacing: 0.8, color: on ? T.gold : 'rgba(246,241,232,0.4)', marginBottom: 3 }}>{t.n}</div>
              <div style={{ fontFamily: T.serif, fontSize: 15, color: on ? T.paper : 'rgba(246,241,232,0.65)', fontStyle: on ? 'italic' : 'normal', position: 'relative', display: 'inline-block' }}>
                {t.label}
                {t.count !== undefined && t.count > 0 && (
                  <span style={{ position: 'absolute', top: -4, right: -14, background: T.gold, color: T.ink, fontFamily: T.mono, fontSize: 8, padding: '1px 5px', borderRadius: 999, lineHeight: 1.3 }}>{t.count}</span>
                )}
              </div>
              {on && <div style={{ position: 'absolute', bottom: 0, left: '25%', right: '25%', height: 2, background: T.gold }} />}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Keep old names as aliases so nothing else breaks during transition
export function MobileTopBar() { return null; }
export function MobileTabBar(_p: { active: Screen; onNav: (s: Screen) => void; fabricsToBuy: number }) { return null; }
