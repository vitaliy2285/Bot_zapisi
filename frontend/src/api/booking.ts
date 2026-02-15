import { api } from './client';
import type { Slot } from '@/types';

export async function fetchSlots(payload: {
  business_id: number;
  service_id: number;
  staff_id: number;
  day: string;
}) {
  const { data } = await api.post<Slot[]>('/booking/slots', payload);
  return data;
}

export async function createBooking(payload: {
  business_id: number;
  service_id: number;
  staff_id: number;
  client_id?: number;
  start_at: string;
  notes?: string;
}) {
  const { data } = await api.post('/booking', payload);
  return data;
}
