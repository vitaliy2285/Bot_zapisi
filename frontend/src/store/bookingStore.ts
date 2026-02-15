import { create } from 'zustand';

type BookingState = {
  serviceId?: number;
  staffId?: number;
  day?: string;
  slotStart?: string;
  clientName: string;
  phone: string;
  setField: <K extends keyof BookingState>(key: K, value: BookingState[K]) => void;
  reset: () => void;
};

const initialState = {
  clientName: '',
  phone: '',
};

export const useBookingStore = create<BookingState>((set) => ({
  ...initialState,
  setField: (key, value) => set((state) => ({ ...state, [key]: value })),
  reset: () => set(initialState),
}));
