import { useState } from 'react';
import type { Client } from './types';
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
  const activeTab: Tab = client ? 'clients' : tab;

  const screen = client
    ? <ProfileScreen key={client.id} client={client} onBack={() => setClient(null)} animClass="push" />
    : tab === 'clients'
      ? <ClientsScreen key="cl" onSelect={setClient} animClass="fade" />
      : tab === 'fabrics'
        ? <FabricsScreen key="fa" animClass="fade" />
        : <ShoppingScreen key="sh" animClass="fade" />;

  return (
    <div className="app-shell">
      <div className="app-body">
        <TabBar active={activeTab} onChange={changeTab} variant="sidebar" />
        <div className="app-screen-wrap">{screen}</div>
      </div>
      <TabBar active={activeTab} onChange={changeTab} variant="bottom" />
    </div>
  );
}
