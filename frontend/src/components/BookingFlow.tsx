import { useMemo, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { createBooking, fetchSlots } from '@/api/booking';
import { useBookingStore } from '@/store/bookingStore';
import { useTelegram } from '@/hooks/useTelegram';
import type { Service, Staff } from '@/types';

const SERVICES: Service[] = [
  { id: 1, business_id: 1, name: 'Haircut', price: '2500', duration_minutes: 60 },
  { id: 2, business_id: 1, name: 'Manicure', price: '1800', duration_minutes: 50 },
];

const STAFF: Staff[] = [
  { id: 1, full_name: 'Anna Petrova', role: 'Top Master' },
  { id: 2, full_name: 'Ivan Smirnov', role: 'Master' },
];

export default function BookingFlow() {
  const [step, setStep] = useState(0);
  const { setField, serviceId, staffId, day, slotStart, clientName, phone, reset } = useBookingStore();
  const { hapticSuccess, hapticError } = useTelegram();

  const dayValue = day ?? format(new Date(), 'yyyy-MM-dd');

  const slotsQuery = useQuery({
    queryKey: ['slots', serviceId, staffId, dayValue],
    queryFn: () =>
      fetchSlots({
        business_id: 1,
        service_id: serviceId!,
        staff_id: staffId!,
        day: dayValue,
      }),
    enabled: Boolean(serviceId && staffId),
  });

  const mutation = useMutation({
    mutationFn: () =>
      createBooking({
        business_id: 1,
        service_id: serviceId!,
        staff_id: staffId!,
        start_at: slotStart!,
        notes: `Client ${clientName}, phone ${phone}`,
      }),
    onSuccess: () => {
      hapticSuccess();
      reset();
      setStep(0);
    },
    onError: () => hapticError(),
  });

  const selectedService = useMemo(() => SERVICES.find((item) => item.id === serviceId), [serviceId]);

  return (
    <div className="mx-auto max-w-md space-y-4 p-4">
      <h1 className="text-2xl font-bold">Book your visit</h1>
      <motion.div key={step} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        {step === 0 && (
          <div className="space-y-3">
            {SERVICES.map((service) => (
              <button
                key={service.id}
                onClick={() => {
                  setField('serviceId', service.id);
                  setStep(1);
                }}
                className="w-full rounded-xl border bg-white p-4 text-left shadow-sm"
              >
                <div className="font-semibold">{service.name}</div>
                <div className="text-sm text-slate-500">{service.duration_minutes} min · {service.price} ₽</div>
              </button>
            ))}
          </div>
        )}

        {step === 1 && (
          <div className="space-y-3">
            <button className="text-sm text-slate-500" onClick={() => setStep(0)}>← Back</button>
            {STAFF.map((member) => (
              <button
                key={member.id}
                onClick={() => {
                  setField('staffId', member.id);
                  setStep(2);
                }}
                className="w-full rounded-xl border bg-white p-4 text-left shadow-sm"
              >
                <div className="font-semibold">{member.full_name}</div>
                <div className="text-sm text-slate-500">{member.role}</div>
              </button>
            ))}
          </div>
        )}

        {step === 2 && (
          <div className="space-y-3">
            <button className="text-sm text-slate-500" onClick={() => setStep(1)}>← Back</button>
            <input
              type="date"
              className="w-full rounded-lg border bg-white p-2"
              value={dayValue}
              onChange={(e) => setField('day', e.target.value)}
            />
            <div className="grid grid-cols-2 gap-2">
              {slotsQuery.data?.map((slot) => (
                <button
                  key={slot.start_at}
                  onClick={() => {
                    setField('slotStart', slot.start_at);
                    setStep(3);
                  }}
                  className="rounded-lg border bg-white p-2 text-sm"
                >
                  {format(new Date(slot.start_at), 'HH:mm')}
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-3">
            <button className="text-sm text-slate-500" onClick={() => setStep(2)}>← Back</button>
            <div className="rounded-xl bg-white p-4 shadow-sm">
              <div className="font-semibold">{selectedService?.name}</div>
              <div className="text-sm text-slate-500">{slotStart ? format(new Date(slotStart), 'dd.MM HH:mm') : '-'}</div>
            </div>
            <input
              placeholder="Your name"
              className="w-full rounded-lg border p-2"
              value={clientName}
              onChange={(e) => setField('clientName', e.target.value)}
            />
            <input
              placeholder="Phone"
              className="w-full rounded-lg border p-2"
              value={phone}
              onChange={(e) => setField('phone', e.target.value)}
            />
            <button
              onClick={() => mutation.mutate()}
              disabled={mutation.isPending || !clientName || !phone || !slotStart}
              className="w-full rounded-lg bg-brand-600 p-3 font-medium text-white disabled:opacity-50"
            >
              {mutation.isPending ? 'Booking...' : 'Confirm booking'}
            </button>
          </div>
        )}
      </motion.div>
    </div>
  );
}
