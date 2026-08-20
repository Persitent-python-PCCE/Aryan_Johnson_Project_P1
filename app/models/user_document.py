from datetime import datetime

from app.extensions import db


class UserDocument(db.Model):
    __tablename__ = "user_documents"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    document_type = db.Column(
        db.String(50),
        nullable=False
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

    user = db.relationship(
        "User",
        back_populates="documents"
    )