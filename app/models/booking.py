from datetime import datetime

from app.extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id"),
        nullable=False,
        index=True
    )

    booking_reference = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    total_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="CONFIRMED",
        index=True
    )

    booked_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    cancelled_at = db.Column(
        db.DateTime,
        nullable=True
    )

    user = db.relationship(
        "User",
        back_populates="bookings"
    )

    event = db.relationship(
        "Event",
        back_populates="bookings"
    )

    items = db.relationship(
        "BookingItem",
        back_populates="booking"
    )