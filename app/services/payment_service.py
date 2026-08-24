from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from app.extensions import db
from app.models.payment import Payment
from app.services.booking_service import BookingService


class PaymentService:

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

    ALLOWED_METHODS = {
        "CARD",
        "UPI"
    }

    @staticmethod
    def create_payment(
        booking_id,
        payment_method
    ):

        booking = BookingService.get_booking(
            booking_id
        )

        if booking.status != (
            BookingService.PENDING_PAYMENT_STATUS
        ):
            raise ValueError(
                "Booking is not awaiting payment"
            )

        if booking.payment:
            raise ValueError(
                "Payment already exists for this booking"
            )

        payment_method = (
            payment_method.upper()
            if payment_method
            else ""
        )

        if payment_method not in (
            PaymentService.ALLOWED_METHODS
        ):
            raise ValueError(
                "Invalid payment method"
            )

        payment = Payment(
            booking_id=booking.id,

            transaction_reference=(
                PaymentService
                ._generate_transaction_reference()
            ),

            amount=Decimal(
                str(booking.total_amount)
            ),

            payment_method=payment_method,

            status=PaymentService.PENDING
        )

        db.session.add(payment)

        db.session.commit()

        return payment

    @staticmethod
    def process_payment(
        booking_id,
        payment_success=True
    ):

        booking = BookingService.get_booking(
            booking_id
        )

        if booking.status != (
            BookingService.PENDING_PAYMENT_STATUS
        ):
            raise ValueError(
                "Booking is not awaiting payment"
            )

        payment = booking.payment

        if not payment:
            raise ValueError(
                "Payment has not been initiated"
            )

        if payment.status != (
            PaymentService.PENDING
        ):
            raise ValueError(
                "Payment has already been processed"
            )

        if payment_success:

            payment.status = (
                PaymentService.SUCCESS
            )

            payment.paid_at = datetime.utcnow()

            booking.status = (
                BookingService.CONFIRMED_STATUS
            )

        else:

            payment.status = (
                PaymentService.FAILED
            )

            booking.status = (
                BookingService.PAYMENT_FAILED_STATUS
            )

        db.session.commit()

        return payment

    @staticmethod
    def _generate_transaction_reference():

        return (
            f"TXN-{uuid4().hex[:12].upper()}"
        )