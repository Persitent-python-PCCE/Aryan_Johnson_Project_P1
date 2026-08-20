from datetime import datetime

from app.extensions import db


class EventPoster(db.Model):
    __tablename__ = "event_posters"

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id"),
        nullable=False,
        index=True
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    stored_filename = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    file_path = db.Column(
        db.String(500),
        nullable=False
    )

    file_size = db.Column(
        db.Integer,
        nullable=False
    )

    mime_type = db.Column(
        db.String(100),
        nullable=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    event = db.relationship(
        "Event",
        back_populates="posters"
    )