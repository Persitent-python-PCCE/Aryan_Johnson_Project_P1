from decimal import Decimal
from uuid import uuid4

from app.extensions import db
from app.repositories.booking_item_repository import BookingItemRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.event_repository import EventRepository
from app.repositories.seat_repository import SeatRepository
from app.repositories.user_repository import UserRepository


class BookingService:

    BOOKABLE_EVENT_STATUS = "PUBLISHED"
    CONFIRMED_STATUS = "CONFIRMED"
    CANCELLED_STATUS = "CANCELLED"

    @staticmethod
    def create_booking(user_id, event_id, seat_ids):
        if not seat_ids:
            raise ValueError(
                "At least one seat must be selected"
            )

        # Remove duplicate seat IDs while preserving order.
        seat_ids = list(dict.fromkeys(seat_ids))

        user = UserRepository.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        event = EventRepository.get_by_id(event_id)

        if not event:
            raise ValueError("Event not found")

        if event.status != BookingService.BOOKABLE_EVENT_STATUS:
            raise ValueError(
                "Event is not available for booking"
            )

        try:
            locked_seats = []

            # Lock every requested seat in deterministic order.
            #
            # Sorting ensures concurrent transactions acquire
            # multiple seat locks in the same order.
            for seat_id in sorted(seat_ids):
                seat = SeatRepository.get_by_id_for_update(
                    seat_id
                )

                if not seat:
                    raise ValueError(
                        f"Seat {seat_id} not found"
                    )

                if not seat.is_active:
                    raise ValueError(
                        f"Seat {seat_id} is inactive"
                    )

                if seat.venue_id != event.venue_id:
                    raise ValueError(
                        f"Seat {seat_id} does not belong "
                        f"to the event venue"
                    )

                locked_seats.append(seat)

            # All requested seat rows are now locked.
            # Check availability only after acquiring the locks.
            available_seats = (
                SeatRepository.get_available_for_event(
                    event_id
                )
            )

            available_seat_ids = {
                seat.id
                for seat in available_seats
            }

            for seat in locked_seats:
                if seat.id not in available_seat_ids:
                    raise ValueError(
                        f"Seat {seat.id} is already booked"
                    )

            # Use Decimal for monetary calculations.
            total_amount = sum(
                (
                    Decimal(str(seat.price))
                    for seat in locked_seats
                ),
                Decimal("0.00")
            )

            booking_reference = (
                BookingService._generate_booking_reference()
            )

            booking = BookingRepository.create(
                user_id=user_id,
                event_id=event_id,
                booking_reference=booking_reference,
                total_amount=total_amount,
                status=BookingService.CONFIRMED_STATUS
            )

            # Create one booking item for every selected seat.
            for seat in locked_seats:
                BookingItemRepository.create(
                    booking_id=booking.id,
                    seat_id=seat.id,
                    price=seat.price
                )

            db.session.commit()

            return booking

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_booking(booking_id):
        booking = BookingRepository.get_by_id(
            booking_id
        )

        if not booking:
            raise ValueError("Booking not found")

        return booking

    @staticmethod
    def get_booking_by_reference(booking_reference):
        booking = BookingRepository.get_by_reference(
            booking_reference
        )

        if not booking:
            raise ValueError("Booking not found")

        return booking

    @staticmethod
    def get_user_bookings(user_id):
        user = UserRepository.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        return BookingRepository.get_by_user(
            user_id
        )

    @staticmethod
    def cancel_booking(booking_id):
        booking = BookingService.get_booking(
            booking_id
        )

        if booking.status != BookingService.CONFIRMED_STATUS:
            raise ValueError(
                "Only confirmed bookings can be cancelled"
            )

        from datetime import datetime

        booking.status = BookingService.CANCELLED_STATUS
        booking.cancelled_at = datetime.utcnow()

        db.session.commit()

        return booking

    @staticmethod
    def _generate_booking_reference():
        return f"BK-{uuid4().hex[:12].upper()}"