from datetime import datetime

from app.extensions import db


class BookingItem(db.Model):
    __tablename__ = "booking_items"

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        nullable=False,
        index=True
    )

    seat_id = db.Column(
        db.Integer,
        db.ForeignKey("seats.id"),
        nullable=False,
        index=True
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    booking = db.relationship(
        "Booking",
        back_populates="items"
    )

    seat = db.relationship(
        "Seat",
        back_populates="booking_items"
    )