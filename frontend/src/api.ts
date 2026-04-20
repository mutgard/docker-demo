const BASE = import.meta.env.VITE_API_URL ?? '';

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`);
  if (!r.ok) throw new Error(`GET ${path} → ${r.status}`);
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

import type { Client, Fabric, ShoppingItem, IntakeData } from './types';

export const api = {
  listClients: () => get<Client[]>('/clients'),
  getClient: (id: number) => get<Client>(`/clients/${id}`),
  patchClient: (id: number, body: Partial<Client>) => patch<Client>(`/clients/${id}`, body),
  patchFabric: (id: number, body: { to_buy?: boolean }) => patch<Fabric>(`/fabrics/${id}`, body),
  getShopping: () => get<ShoppingItem[]>('/shopping'),
  getIntake: async (id: number): Promise<IntakeData | null> => {
    const r = await fetch(`${BASE}/clients/${id}/intake`);
    if (r.status === 404) return null;
    if (!r.ok) throw new Error(`GET /clients/${id}/intake → ${r.status}`);
    return r.json();
  },
};
