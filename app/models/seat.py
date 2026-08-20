from app.extensions import db


class Seat(db.Model):
    __tablename__ = "seats"

    id = db.Column(db.Integer, primary_key=True)

    venue_id = db.Column(
        db.Integer,
        db.ForeignKey("venues.id"),
        nullable=False,
        index=True
    )

    seat_number = db.Column(
        db.String(20),
        nullable=False
    )

    row_number = db.Column(
        db.Integer,
        nullable=False
    )

    seat_type = db.Column(
        db.String(20),
        nullable=False,
        default="REGULAR"
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    venue = db.relationship(
        "Venue",
        back_populates="seats"
    )

    booking_items = db.relationship(
        "BookingItem",
        back_populates="seat"
    )