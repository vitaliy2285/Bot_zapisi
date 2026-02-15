export type Service = {
  id: number;
  business_id: number;
  name: string;
  price: string;
  duration_minutes: number;
};

export type Staff = {
  id: number;
  full_name: string;
  role: string;
  avatar_url?: string;
};

export type Slot = {
  start_at: string;
  end_at: string;
};

export type BookingCard = {
  id: number;
  clientName: string;
  serviceName: string;
  staffName: string;
  startAt: string;
  status: 'pending' | 'confirmed' | 'paid' | 'no_show' | 'completed';
};
