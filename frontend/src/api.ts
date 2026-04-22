const BASE = import.meta.env.VITE_API_URL ?? '';

import type {
  Client, Fabric, ShoppingItem, IntakeData, ClientBrief, ClientCreate,
  AtelierEvent, AppointmentCreate, DeliveryCreate,
  DemoScenarioSummary, DemoScenario,
} from './types';

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`);
  if (!r.ok) throw new Error(`GET ${path} → ${r.status}`);
  return r.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`POST ${path} → ${r.status}`);
  return r.json();
}

async function patch<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`PATCH ${path} → ${r.status}`);
  return r.json();
}

async function del(path: string): Promise<void> {
  const r = await fetch(`${BASE}${path}`, { method: 'DELETE' });
  if (!r.ok) throw new Error(`DELETE ${path} → ${r.status}`);
}

export const api = {
  listClients:   () => get<Client[]>('/clients'),
  getClient:     (id: number) => get<Client>(`/clients/${id}`),
  createClient:  (body: ClientCreate) => post<Client>('/clients', body),
  patchClient:   (id: number, body: Partial<Client>) => patch<Client>(`/clients/${id}`, body),
  patchFabric:   (id: number, body: { to_buy?: boolean }) => patch<Fabric>(`/fabrics/${id}`, body),
  getShopping:   () => get<ShoppingItem[]>('/shopping'),

  listEvents: (from: string, to: string, clientId?: number) => {
    const q = clientId != null ? `&client_id=${clientId}` : '';
    return get<AtelierEvent[]>(`/events?from=${from}&to=${to}${q}`);
  },

  createAppointment: (body: AppointmentCreate) =>
    post<AtelierEvent>('/appointments', body),
  updateAppointment: (id: number, body: Partial<AppointmentCreate>) =>
    patch<AtelierEvent>(`/appointments/${id}`, body),
  deleteAppointment: (id: number) =>
    del(`/appointments/${id}`),

  createDelivery: (body: DeliveryCreate) =>
    post<AtelierEvent>('/deliveries', body),
  updateDelivery: (id: number, body: Partial<DeliveryCreate>) =>
    patch<AtelierEvent>(`/deliveries/${id}`, body),
  deleteDelivery: (id: number) =>
    del(`/deliveries/${id}`),

  getIntake: async (id: number): Promise<IntakeData | null> => {
    const r = await fetch(`${BASE}/clients/${id}/intake`);
    if (r.status === 404) return null;
    if (!r.ok) throw new Error(`GET /clients/${id}/intake → ${r.status}`);
    return r.json();
  },

  getBrief: async (token: string): Promise<ClientBrief | null> => {
    const r = await fetch(`${BASE}/api/brief/${token}`);
    if (r.status === 404) return null;
    if (!r.ok) throw new Error(`GET /api/brief/${token} → ${r.status}`);
    return r.json();
  },

  listDemoScenarios: () => get<DemoScenarioSummary[]>('/demo-scenarios'),
  getDemoScenario:   (id: string) => get<DemoScenario>(`/demo-scenarios/${id}`),
};
