from app.extensions import db
from app.models.booking_item import BookingItem


class BookingItemRepository:

    @staticmethod
    def create(
        booking_id,
        seat_id,
        price
    ):
        booking_item = BookingItem(
            booking_id=booking_id,
            seat_id=seat_id,
            price=price
        )

        db.session.add(booking_item)
        db.session.flush()

        return booking_item

    @staticmethod
    def get_by_id(booking_item_id):
        return db.session.get(
            BookingItem,
            booking_item_id
        )

    @staticmethod
    def get_by_booking(booking_id):
        return (
            BookingItem.query
            .filter(
                BookingItem.booking_id == booking_id
            )
            .order_by(
                BookingItem.id.asc()
            )
            .all()
        )

    @staticmethod
    def get_by_seat(seat_id):
        return (
            BookingItem.query
            .filter(
                BookingItem.seat_id == seat_id
            )
            .order_by(
                BookingItem.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def delete(booking_item):
        db.session.delete(booking_item)
        db.session.flush()