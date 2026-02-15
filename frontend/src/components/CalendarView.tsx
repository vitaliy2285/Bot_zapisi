import { useMemo, useState } from 'react';
import { addMinutes, format, startOfDay } from 'date-fns';
import type { BookingCard } from '@/types';

const INITIAL_BOOKINGS: BookingCard[] = [
  {
    id: 1,
    clientName: 'Olga Ivanova',
    serviceName: 'Haircut',
    staffName: 'Anna Petrova',
    startAt: new Date().toISOString(),
    status: 'confirmed',
  },
  {
    id: 2,
    clientName: 'Maria Kozlova',
    serviceName: 'Manicure',
    staffName: 'Ivan Smirnov',
    startAt: addMinutes(new Date(), 90).toISOString(),
    status: 'pending',
  },
];

export default function CalendarView() {
  const [bookings, setBookings] = useState(INITIAL_BOOKINGS);
  const timeGrid = useMemo(() => {
    const dayStart = startOfDay(new Date());
    return Array.from({ length: 24 }, (_, i) => format(addMinutes(dayStart, i * 60), 'HH:mm'));
  }, []);

  function moveBooking(id: number, minutesDelta: number) {
    setBookings((prev) =>
      prev.map((item) =>
        item.id === id
          ? {
              ...item,
              startAt: addMinutes(new Date(item.startAt), minutesDelta).toISOString(),
            }
          : item,
      ),
    );
  }

  return (
    <div className="p-4">
      <h2 className="mb-4 text-xl font-bold">Admin Scheduler</h2>
      <div className="grid grid-cols-[80px_1fr] rounded-lg border bg-white">
        <div className="border-r">
          {timeGrid.map((time) => (
            <div key={time} className="h-16 border-b px-2 py-1 text-xs text-slate-500">
              {time}
            </div>
          ))}
        </div>
        <div className="relative min-h-[1536px]">
          {bookings.map((booking) => {
            const date = new Date(booking.startAt);
            const top = date.getHours() * 64 + date.getMinutes();
            return (
              <div
                key={booking.id}
                className="absolute left-2 right-2 rounded-lg border-l-4 border-brand-600 bg-brand-50 p-2"
                style={{ top, height: 72 }}
              >
                <div className="text-sm font-semibold">{booking.clientName}</div>
                <div className="text-xs text-slate-600">{booking.serviceName} · {booking.staffName}</div>
                <div className="mt-1 flex gap-2">
                  <button className="rounded border px-2 text-xs" onClick={() => moveBooking(booking.id, -15)}>
                    -15m
                  </button>
                  <button className="rounded border px-2 text-xs" onClick={() => moveBooking(booking.id, 15)}>
                    +15m
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
