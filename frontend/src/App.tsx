import { useState, useEffect } from 'react';
import type { Client } from './types';
import { T } from './tokens';
import { useIsMobile } from './hooks/useIsMobile';
import { Sidebar } from './components/Sidebar';
import { MobileHeader } from './components/MobileShell';
import { ClientsScreen } from './screens/ClientsScreen';
import { ProfileScreen } from './screens/ProfileScreen';
import { FabricsScreen } from './screens/FabricsScreen';
import { ShoppingScreen } from './screens/ShoppingScreen';
import { api } from './api';

type Screen = 'clients' | 'profile' | 'fabrics' | 'shop';

export default function App() {
  const mobile = useIsMobile();
  const [screen, setScreen] = useState<Screen>('clients');
  const [clientId, setClientId] = useState<number | null>(null);
  const [clients, setClients] = useState<Client[]>([]);

  useEffect(() => { api.listClients().then(setClients); }, []);

  const fabricsToBuy = clients.flatMap(c => c.fabrics).filter(f => f.to_buy).length;
  const totalFabrics = clients.flatMap(c => c.fabrics).length;

  const nav = (s: Screen) => { setScreen(s); if (s !== 'profile') setClientId(null); };
  const openClient = (id: number) => { setClientId(id); setScreen('profile'); };
  const back = () => { setScreen('clients'); setClientId(null); };
  const refresh = () => api.listClients().then(setClients);

  const content = (
    <>
      {screen === 'clients' && <ClientsScreen clients={clients} onOpen={openClient} />}
      {screen === 'profile' && clientId !== null && (
        <ProfileScreen
          client={clients.find(c => c.id === clientId) ?? clients[0]}
          onBack={back}
          onOpenFabrics={() => nav('fabrics')}
          onRefresh={refresh}
        />
      )}
      {screen === 'fabrics' && <FabricsScreen clients={clients} onRefresh={refresh} />}
      {screen === 'shop'    && <ShoppingScreen clients={clients} />}
    </>
  );

  if (mobile) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100dvh', background: T.paper, color: T.ink, fontFamily: T.sans }}>
        <MobileHeader active={screen} onNav={nav} fabricsToBuy={fabricsToBuy} />
        <div style={{ flex: 1, minHeight: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', paddingBottom: 'env(safe-area-inset-bottom)' }}>{content}</div>
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '232px 1fr', width: '100%', height: '100%', background: T.paper, color: T.ink, fontFamily: T.sans }}>
      <Sidebar active={screen} onNav={nav} fabricsToBuy={fabricsToBuy} totalClients={clients.length} totalFabrics={totalFabrics} />
      <div style={{ minWidth: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>{content}</div>
    </div>
  );
}
