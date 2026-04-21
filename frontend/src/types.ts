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

export interface IntakeBrief {
  wedding_date: string;
  venue: string;
  garment: string;
  style: string;
  budget_tier: string;
  fabric_notes: string;
  extra_notes: string;
}

export interface IntakeDocument {
  label: string;
  type: string;
  url: string | null;
}

export interface WhatsAppMessage {
  role: 'client' | 'julia';
  text: string;
  time: string;
}

export interface WhatsAppIntake {
  source: 'whatsapp';
  token?: string;
  thread: WhatsAppMessage[];
  brief: IntakeBrief;
  documents: IntakeDocument[];
}

export interface WebFormIntake {
  source: 'web_form';
  token?: string;
  submitted_at: string;
  form_data: Record<string, string>;
  brief: IntakeBrief;
  documents: IntakeDocument[];
}

export type IntakeData = WhatsAppIntake | WebFormIntake;

export interface ClientBrief {
  client_name: string;
  wedding_date: string;
  venue: string;
  garment: string;
  style: string;
  fabric_notes: string;
}
