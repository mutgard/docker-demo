import { useState } from 'react';
import type { Client } from './types';
import { StatusBar } from './components/StatusBar';
import { TabBar } from './components/TabBar';
import { ClientsScreen } from './screens/ClientsScreen';
import { ProfileScreen } from './screens/ProfileScreen';
import { FabricsScreen } from './screens/FabricsScreen';
import { ShoppingScreen } from './screens/ShoppingScreen';

type Tab = 'clients' | 'fabrics' | 'shop';

export default function App() {
  const [tab, setTab] = useState<Tab>('clients');
  const [client, setClient] = useState<Client | null>(null);

  const changeTab = (t: Tab) => { setClient(null); setTab(t); };

  return (
    <div style={{
      width: '100vw', height: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', background: 'var(--bg-canvas)', padding: 16,
    }}>
      <div style={{
        width: 390, height: 844, borderRadius: 54, background: 'var(--bg-app)',
        border: '7px solid #221e1a',
        boxShadow: '0 0 0 1px rgba(0,0,0,.18),0 32px 80px rgba(0,0,0,.28)',
        position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column',
      }}>
        <div style={{
          position: 'absolute', top: 0, left: '50%', transform: 'translateX(-50%)',
          width: 128, height: 34, background: '#221e1a',
          borderBottomLeftRadius: 18, borderBottomRightRadius: 18, zIndex: 10,
        }}/>
        <StatusBar />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {client
            ? <ProfileScreen key={client.id} client={client} onBack={() => setClient(null)} animClass="push" />
            : tab === 'clients'
              ? <ClientsScreen key="cl" onSelect={setClient} animClass="fade" />
              : tab === 'fabrics'
                ? <FabricsScreen key="fa" animClass="fade" />
                : <ShoppingScreen key="sh" animClass="fade" />}
        </div>
        <TabBar active={client ? 'clients' : tab} onChange={changeTab} />
      </div>
    </div>
  );
}
