from datetime import datetime

from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        nullable=False,
        unique=True,
        index=True
    )

    transaction_reference = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
        index=True
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    payment_method = db.Column(
        db.String(30),
        nullable=False,
        default="MOCK"
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="PENDING",
        index=True
    )

    paid_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    booking = db.relationship(
        "Booking",
        back_populates="payment"
    )