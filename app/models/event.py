from datetime import datetime

from app.extensions import db


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False,
        index=True
    )

    venue_id = db.Column(
        db.Integer,
        db.ForeignKey("venues.id"),
        nullable=False,
        index=True
    )

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    event_date = db.Column(
        db.Date,
        nullable=False,
        index=True
    )

    start_time = db.Column(
        db.Time,
        nullable=False
    )

    end_time = db.Column(
        db.Time,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="DRAFT",
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    category = db.relationship(
        "Category",
        back_populates="events"
    )

    venue = db.relationship(
        "Venue",
        back_populates="events"
    )

    bookings = db.relationship(
        "Booking",
        back_populates="event"
    )

    posters = db.relationship(
        "EventPoster",
        back_populates="event"
    )