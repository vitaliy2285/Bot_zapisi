from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Booking, BookingSource, BookingStatus, Service
from app.schemas.booking import BookingCreate, BookingOut, SlotOut, SlotQuery
from app.services.slot_finder import find_free_slots

router = APIRouter(prefix="/booking", tags=["booking"])


@router.post("/slots", response_model=list[SlotOut])
async def list_slots(payload: SlotQuery, db: AsyncSession = Depends(get_db)) -> list[SlotOut]:
    slots = await find_free_slots(
        db=db,
        business_id=payload.business_id,
        service_id=payload.service_id,
        staff_id=payload.staff_id,
        day=payload.day,
        step_minutes=payload.step_minutes,
    )
    return [SlotOut(start_at=start, end_at=end) for start, end in slots]


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(payload: BookingCreate, db: AsyncSession = Depends(get_db)) -> BookingOut:
    service = await db.scalar(
        select(Service).where(and_(Service.id == payload.service_id, Service.business_id == payload.business_id, Service.is_active))
    )
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    end_at = payload.start_at + timedelta(minutes=service.duration_minutes)

    conflict = await db.scalar(
        select(Booking).where(
            and_(
                Booking.staff_id == payload.staff_id,
                Booking.start_at < end_at,
                Booking.end_at > payload.start_at,
                Booking.status.in_([BookingStatus.pending, BookingStatus.confirmed, BookingStatus.paid]),
            )
        )
    )
    if conflict:
        raise HTTPException(status_code=409, detail="Timeslot is no longer available")

    booking = Booking(
        business_id=payload.business_id,
        service_id=payload.service_id,
        staff_id=payload.staff_id,
        client_id=payload.client_id,
        start_at=payload.start_at,
        end_at=end_at,
        status=BookingStatus.pending,
        source=BookingSource.telegram,
        notes=payload.notes,
        total_price=service.price,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return BookingOut.model_validate(booking)
