from app.extensions import db
from app.models.event_poster import EventPoster


class EventPosterRepository:

    @staticmethod
    def create(
        event_id,
        original_filename,
        stored_filename,
        file_path,
        file_size,
        mime_type
    ):
        poster = EventPoster(
            event_id=event_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type
        )

        db.session.add(poster)
        db.session.flush()

        return poster

    @staticmethod
    def get_by_id(poster_id):
        return db.session.get(EventPoster, poster_id)

    @staticmethod
    def get_by_event(event_id):
        return (
            EventPoster.query
            .filter(
                EventPoster.event_id == event_id
            )
            .order_by(
                EventPoster.uploaded_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_stored_filename(stored_filename):
        return (
            EventPoster.query
            .filter(
                EventPoster.stored_filename == stored_filename
            )
            .first()
        )

    @staticmethod
    def update(poster, **kwargs):
        for field, value in kwargs.items():
            if hasattr(poster, field):
                setattr(poster, field, value)

        db.session.flush()

        return poster

    @staticmethod
    def delete(poster):
        db.session.delete(poster)
        db.session.flush()