from decimal import Decimal, InvalidOperation

from app.repositories.seat_repository import SeatRepository
from app.repositories.venue_repository import VenueRepository
from app.repositories.event_repository import EventRepository


class SeatService:

    VALID_SEAT_TYPES = {
        "REGULAR",
        "PREMIUM",
        "VIP"
    }

    @staticmethod
    def get_seats_by_venue(venue_id):
        venue = VenueRepository.get_by_id(venue_id)

        if not venue:
            raise ValueError("Venue not found")

        return SeatRepository.get_by_venue(
            venue_id,
            active_only=False
        )

    @staticmethod
    def get_seat(seat_id):
        seat = SeatRepository.get_by_id(seat_id)

        if not seat:
            raise ValueError("Seat not found")

        return seat

    @staticmethod
    def create_seat(
        venue_id,
        seat_number,
        row_number,
        seat_type,
        price,
        is_active=True
    ):
        venue = VenueRepository.get_by_id(venue_id)

        if not venue:
            raise ValueError("Venue not found")

        if not seat_number or not seat_number.strip():
            raise ValueError("Seat number is required")

        try:
            row_number = int(row_number)
        except (TypeError, ValueError):
            raise ValueError("Row number must be a valid integer")

        if row_number <= 0:
            raise ValueError(
                "Row number must be greater than zero"
            )

        seat_type = (seat_type or "REGULAR").strip().upper()

        if seat_type not in SeatService.VALID_SEAT_TYPES:
            raise ValueError("Invalid seat type")

        try:
            price = Decimal(str(price))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Price must be a valid number")

        if price < Decimal("0.00"):
            raise ValueError("Price cannot be negative")

        seat_number = seat_number.strip().upper()

        existing_seats = SeatRepository.get_by_venue(
            venue_id
        )

        if any(
            seat.seat_number.upper() == seat_number
            for seat in existing_seats
        ):
            raise ValueError(
                "A seat with this seat number already exists"
            )

        return SeatRepository.create(
            venue_id=venue_id,
            seat_number=seat_number,
            row_number=row_number,
            seat_type=seat_type,
            price=price,
            is_active=is_active
        )

    @staticmethod
    def update_seat(
        seat_id,
        seat_number,
        row_number,
        seat_type,
        price,
        is_active=True
    ):
        seat = SeatService.get_seat(seat_id)

        if not seat_number or not seat_number.strip():
            raise ValueError("Seat number is required")

        try:
            row_number = int(row_number)
        except (TypeError, ValueError):
            raise ValueError("Row number must be a valid integer")

        if row_number <= 0:
            raise ValueError(
                "Row number must be greater than zero"
            )

        seat_type = (seat_type or "REGULAR").strip().upper()

        if seat_type not in SeatService.VALID_SEAT_TYPES:
            raise ValueError("Invalid seat type")

        try:
            price = Decimal(str(price))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Price must be a valid number")

        if price < Decimal("0.00"):
            raise ValueError("Price cannot be negative")

        seat_number = seat_number.strip().upper()

        existing_seats = SeatRepository.get_by_venue(
            seat.venue_id
        )

        for existing in existing_seats:
            if (
                existing.id != seat.id
                and existing.seat_number.upper() == seat_number
            ):
                raise ValueError(
                    "A seat with this seat number already exists"
                )

        return SeatRepository.update(
            seat,
            seat_number=seat_number,
            row_number=row_number,
            seat_type=seat_type,
            price=price,
            is_active=is_active
        )

    @staticmethod
    def delete_seat(seat_id):
        seat = SeatService.get_seat(seat_id)

        if seat.booking_items:
            raise ValueError(
                "Cannot delete a seat that has booking history"
            )

        SeatRepository.delete(seat)

        return True

    @staticmethod
    def get_event_seat_summary(event_id):
        available = SeatRepository.get_available_for_event(
            event_id
        )

        total = SeatRepository.count_by_venue(
            available[0].venue_id
        ) if available else 0

        return {
            "available": len(available),
            "total": total
        }

    @staticmethod
    def get_available_seats(event_id):
        return SeatRepository.get_available_for_event(
            event_id
        )

    @staticmethod
    def get_event_seat_summary(event_id):
        event = EventRepository.get_by_id(event_id)

        if not event:
            raise ValueError("Event not found")

        total = SeatRepository.count_by_venue(
            event.venue_id
        )

        available = SeatRepository.count_available_for_event(
            event_id
        )

        return {
            "available": available,
            "total": total
        }