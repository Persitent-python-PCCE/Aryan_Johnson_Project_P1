from app.extensions import db
from app.models.booking import Booking


class BookingRepository:

    @staticmethod
    def create(
        user_id,
        event_id,
        booking_reference,
        total_amount,
        status="CONFIRMED"
    ):
        booking = Booking(
            user_id=user_id,
            event_id=event_id,
            booking_reference=booking_reference,
            total_amount=total_amount,
            status=status
        )

        db.session.add(booking)
        db.session.flush()

        return booking

    @staticmethod
    def get_by_id(booking_id):
        return db.session.get(
            Booking,
            booking_id
        )

    @staticmethod
    def get_by_reference(booking_reference):
        return (
            Booking.query
            .filter(
                Booking.booking_reference == booking_reference
            )
            .first()
        )

    @staticmethod
    def get_by_user(user_id):
        return (
            Booking.query
            .filter(
                Booking.user_id == user_id
            )
            .order_by(
                Booking.booked_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_event(event_id):
        return (
            Booking.query
            .filter(
                Booking.event_id == event_id
            )
            .order_by(
                Booking.booked_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_confirmed_by_event(event_id):
        return (
            Booking.query
            .filter(
                Booking.event_id == event_id,
                Booking.status == "CONFIRMED"
            )
            .order_by(
                Booking.booked_at.desc()
            )
            .all()
        )

    @staticmethod
    def search(
        booking_reference=None,
        user_id=None,
        event_id=None,
        status=None,
        page=1,
        per_page=10
    ):
        query = Booking.query

        if booking_reference:
            query = query.filter(
                Booking.booking_reference.ilike(
                    f"%{booking_reference}%"
                )
            )

        if user_id is not None:
            query = query.filter(
                Booking.user_id == user_id
            )

        if event_id is not None:
            query = query.filter(
                Booking.event_id == event_id
            )

        if status is not None:
            query = query.filter(
                Booking.status == status
            )

        return (
            query
            .order_by(
                Booking.booked_at.desc()
            )
            .paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        )

    @staticmethod
    def update(booking, **kwargs):
        for field, value in kwargs.items():
            if hasattr(booking, field):
                setattr(
                    booking,
                    field,
                    value
                )

        db.session.flush()

        return booking

    @staticmethod
    def delete(booking):
        db.session.delete(booking)
        db.session.flush()