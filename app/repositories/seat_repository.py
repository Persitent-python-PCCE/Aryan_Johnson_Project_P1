from sqlalchemy import and_, exists

from app.extensions import db
from app.models.booking import Booking
from app.models.booking_item import BookingItem
from app.models.event import Event
from app.models.seat import Seat


class SeatRepository:

    @staticmethod
    def create(
        venue_id,
        seat_number,
        row_number,
        seat_type,
        price,
        is_active=True
    ):
        seat = Seat(
            venue_id=venue_id,
            seat_number=seat_number,
            row_number=row_number,
            seat_type=seat_type,
            price=price,
            is_active=is_active
        )

        db.session.add(seat)
        db.session.flush()

        return seat

    @staticmethod
    def get_by_id(seat_id):
        return db.session.get(Seat, seat_id)

    @staticmethod
    def get_by_venue(venue_id, active_only=False):
        query = Seat.query.filter(
            Seat.venue_id == venue_id
        )

        if active_only:
            query = query.filter(
                Seat.is_active.is_(True)
            )

        return (
            query
            .order_by(
                Seat.row_number.asc(),
                Seat.seat_number.asc()
            )
            .all()
        )

    @staticmethod
    def get_available_for_event(event_id):
        booked_seat_exists = exists().where(
            and_(
                BookingItem.seat_id == Seat.id,
                BookingItem.booking_id == Booking.id,
                Booking.event_id == event_id,
                Booking.status == "CONFIRMED"
            )
        )

        return (
            Seat.query
            .join(
                Event,
                Event.venue_id == Seat.venue_id
            )
            .filter(Event.id == event_id)
            .filter(Seat.is_active.is_(True))
            .filter(~booked_seat_exists)
            .order_by(
                Seat.row_number.asc(),
                Seat.seat_number.asc()
            )
            .all()
        )

    @staticmethod
    def update(seat, **kwargs):
        for field, value in kwargs.items():
            if hasattr(seat, field):
                setattr(seat, field, value)

        db.session.flush()

        return seat

    @staticmethod
    def delete(seat):
        db.session.delete(seat)
        db.session.flush()

    @staticmethod
    def get_by_id_for_update(seat_id):
        return (
        db.session.query(Seat)
        .filter(Seat.id == seat_id)
        .with_for_update()
        .first()
    )