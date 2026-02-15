from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Booking, BookingStatus, Business, Schedule, ScheduleType, Service

BLOCKING_BOOKING_STATUSES = {
    BookingStatus.pending,
    BookingStatus.confirmed,
    BookingStatus.paid,
    BookingStatus.completed,
}


def _overlaps(candidate_start: datetime, candidate_end: datetime, blocked_start: datetime, blocked_end: datetime) -> bool:
    return candidate_start < blocked_end and blocked_start < candidate_end


async def find_free_slots(
    db: AsyncSession,
    business_id: int,
    service_id: int,
    staff_id: int,
    day,
    step_minutes: int = 15,
) -> list[tuple[datetime, datetime]]:
    business = await db.scalar(select(Business).where(Business.id == business_id))
    service = await db.scalar(select(Service).where(and_(Service.id == service_id, Service.business_id == business_id)))
    if not business or not service:
        return []

    tz = ZoneInfo(business.timezone)

    schedules = (
        await db.scalars(
            select(Schedule).where(and_(Schedule.staff_id == staff_id, Schedule.day == day)).order_by(Schedule.start_time)
        )
    ).all()
    work_ranges: list[tuple[datetime, datetime]] = []
    break_ranges: list[tuple[datetime, datetime]] = []

    for schedule in schedules:
        start = datetime.combine(day, schedule.start_time, tzinfo=tz)
        end = datetime.combine(day, schedule.end_time, tzinfo=tz)
        if schedule.schedule_type == ScheduleType.work:
            work_ranges.append((start, end))
        elif schedule.schedule_type == ScheduleType.break_time:
            break_ranges.append((start, end))
        elif schedule.schedule_type == ScheduleType.day_off:
            return []

    if not work_ranges:
        return []

    day_start = min(start for start, _ in work_ranges)
    day_end = max(end for _, end in work_ranges)

    bookings = (
        await db.scalars(
            select(Booking).where(
                and_(
                    Booking.staff_id == staff_id,
                    Booking.start_at < day_end,
                    Booking.end_at > day_start,
                    Booking.status.in_(BLOCKING_BOOKING_STATUSES),
                )
            )
        )
    ).all()

    blocked_ranges = [(b.start_at.astimezone(tz), b.end_at.astimezone(tz)) for b in bookings]
    blocked_ranges.extend(break_ranges)

    service_duration = timedelta(minutes=service.duration_minutes)
    step = timedelta(minutes=step_minutes)
    slots: list[tuple[datetime, datetime]] = []

    for work_start, work_end in work_ranges:
        candidate_start = work_start
        while candidate_start + service_duration <= work_end:
            candidate_end = candidate_start + service_duration
            if not any(_overlaps(candidate_start, candidate_end, blocked_start, blocked_end) for blocked_start, blocked_end in blocked_ranges):
                slots.append((candidate_start, candidate_end))
            candidate_start += step

    now_tz = datetime.now(tz)
    return [(slot_start, slot_end) for slot_start, slot_end in slots if slot_start > now_tz]
