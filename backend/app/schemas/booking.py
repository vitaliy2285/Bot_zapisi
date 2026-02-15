from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models import BookingStatus


class SlotOut(BaseModel):
    start_at: datetime
    end_at: datetime


class SlotQuery(BaseModel):
    business_id: int
    service_id: int
    staff_id: int
    day: date
    step_minutes: int = Field(default=15, ge=5, le=60)


class BookingCreate(BaseModel):
    business_id: int
    service_id: int
    staff_id: int
    client_id: int | None = None
    start_at: datetime
    notes: str | None = None


class BookingOut(BaseModel):
    id: int
    start_at: datetime
    end_at: datetime
    status: BookingStatus

    model_config = {"from_attributes": True}
