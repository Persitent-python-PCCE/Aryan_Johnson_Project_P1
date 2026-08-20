from app.repositories.event_repository import EventRepository
from app.repositories.seat_repository import SeatRepository
from app.repositories.venue_repository import VenueRepository


class SeatService:

    ALLOWED_SEAT_TYPES = {
        "REGULAR",
        "PREMIUM",
        "VIP"
    }

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

        if row_number <= 0:
            raise ValueError(
                "Row number must be greater than zero"
            )

        if price < 0:
            raise ValueError(
                "Seat price cannot be negative"
            )

        if seat_type not in SeatService.ALLOWED_SEAT_TYPES:
            raise ValueError("Invalid seat type")

        existing_seats = SeatRepository.get_by_venue(
            venue_id
        )

        if any(
            seat.seat_number == seat_number
            for seat in existing_seats
        ):
            raise ValueError(
                "Seat number already exists for this venue"
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
    def get_seat(seat_id):
        seat = SeatRepository.get_by_id(seat_id)

        if not seat:
            raise ValueError("Seat not found")

        return seat

    @staticmethod
    def get_venue_seats(
        venue_id,
        active_only=False
    ):
        venue = VenueRepository.get_by_id(venue_id)

        if not venue:
            raise ValueError("Venue not found")

        return SeatRepository.get_by_venue(
            venue_id,
            active_only=active_only
        )

    @staticmethod
    def get_available_seats(event_id):
        event = EventRepository.get_by_id(event_id)

        if not event:
            raise ValueError("Event not found")

        return SeatRepository.get_available_for_event(
            event_id
        )

    @staticmethod
    def update_seat(seat_id, **kwargs):
        seat = SeatService.get_seat(seat_id)

        if "row_number" in kwargs:
            if kwargs["row_number"] <= 0:
                raise ValueError(
                    "Row number must be greater than zero"
                )

        if "price" in kwargs:
            if kwargs["price"] < 0:
                raise ValueError(
                    "Seat price cannot be negative"
                )

        if "seat_type" in kwargs:
            if kwargs["seat_type"] not in SeatService.ALLOWED_SEAT_TYPES:
                raise ValueError("Invalid seat type")

        if "seat_number" in kwargs:
            existing_seats = SeatRepository.get_by_venue(
                seat.venue_id
            )

            for existing_seat in existing_seats:
                if (
                    existing_seat.id != seat.id
                    and existing_seat.seat_number
                    == kwargs["seat_number"]
                ):
                    raise ValueError(
                        "Seat number already exists for this venue"
                    )

        return SeatRepository.update(
            seat,
            **kwargs
        )

    @staticmethod
    def deactivate_seat(seat_id):
        seat = SeatService.get_seat(seat_id)

        return SeatRepository.update(
            seat,
            is_active=False
        )