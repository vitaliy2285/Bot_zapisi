from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Booking, BookingStatus, PaymentMethod, Transaction, TransactionType

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/yookassa")
async def yookassa_webhook(
    event: dict,
    db: AsyncSession = Depends(get_db),
    x_request_id: str | None = Header(default=None),
) -> dict:
    if not x_request_id:
        raise HTTPException(status_code=400, detail="Missing X-Request-Id")

    obj = event.get("object", {})
    payment_id = obj.get("id")
    status = obj.get("status")
    amount_data = obj.get("amount", {})
    metadata = obj.get("metadata", {})
    booking_id = metadata.get("booking_id")

    if not payment_id or not booking_id:
        raise HTTPException(status_code=400, detail="Invalid payment payload")

    existing_tx = await db.scalar(select(Transaction).where(Transaction.external_payment_id == payment_id))
    if existing_tx:
        return {"ok": True, "idempotent": True}

    booking = await db.scalar(select(Booking).where(Booking.id == int(booking_id)))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    amount = Decimal(amount_data.get("value", "0"))

    if status == "succeeded":
        booking.status = BookingStatus.paid
        transaction_type = TransactionType.payment
    elif status == "canceled":
        booking.status = BookingStatus.confirmed
        transaction_type = TransactionType.refund
    else:
        return {"ok": True, "ignored": True}

    tx = Transaction(
        booking_id=booking.id,
        amount=amount,
        transaction_type=transaction_type,
        payment_method=PaymentMethod.yookassa,
        external_payment_id=payment_id,
    )
    db.add(tx)
    await db.commit()

    return {"ok": True}
