export type ClientStatus = 'prospect' | 'sense-paga' | 'clienta' | 'entregada';

export interface Fabric {
  id: number;
  name: string;
  use: string;
  qty: string;
  price: string;
  to_buy: boolean;
  supplier: string;
}

export interface Appointment {
  id: number;
  label: string;
  value: string;
}

export interface Payment {
  id: number;
  label: string;
  value: string;
}

export interface Client {
  id: number;
  name: string;
  wedding_date: string;
  days_until: number;
  status: ClientStatus;
  garment: string;
  garment_style: string;
  measurements_date: string;
  phone: string;
  email: string;
  notes: string;
  fabrics: Fabric[];
  appointments: Appointment[];
  payments: Payment[];
}

export interface ShoppingItem extends Fabric {
  client_id: number;
  client_name: string;
}
