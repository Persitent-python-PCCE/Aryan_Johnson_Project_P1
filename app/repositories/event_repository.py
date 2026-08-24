from app.extensions import db
from app.models.event import Event
from app.models.booking import Booking


class EventRepository:

    @staticmethod
    def create(
        category_id,
        venue_id,
        name,
        description,
        event_date,
        start_time,
        end_time,
        status="DRAFT"
    ):
        event = Event(
            category_id=category_id,
            venue_id=venue_id,
            name=name,
            description=description,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            status=status
        )

        db.session.add(event)
        db.session.flush()

        return event

    @staticmethod
    def get_by_id(event_id):
        return db.session.get(Event, event_id)

    @staticmethod
    def get_all():
        return (
            Event.query
            .order_by(
                Event.event_date.asc(),
                Event.start_time.asc()
            )
            .all()
        )

    @staticmethod
    def get_by_category(category_id):
        return (
            Event.query
            .filter(Event.category_id == category_id)
            .order_by(Event.event_date.asc())
            .all()
        )

    @staticmethod
    def get_by_venue(venue_id):
        return (
            Event.query
            .filter(Event.venue_id == venue_id)
            .order_by(Event.event_date.asc())
            .all()
        )

    @staticmethod
    def get_by_status(status):
        return (
            Event.query
            .filter(Event.status == status)
            .order_by(Event.event_date.asc())
            .all()
        )

    @staticmethod
    def search(
        keyword=None,
        category_id=None,
        venue_id=None,
        event_date=None,
        status=None,
        page=1,
        per_page=10
    ):
        query = Event.query

        if keyword:
            query = query.filter(
                Event.name.ilike(f"%{keyword}%")
            )

        if category_id is not None:
            query = query.filter(
                Event.category_id == category_id
            )

        if venue_id is not None:
            query = query.filter(
                Event.venue_id == venue_id
            )

        if event_date is not None:
            query = query.filter(
                Event.event_date == event_date
            )

        if status is not None:
            query = query.filter(
                Event.status == status
            )

        return (
            query
            .order_by(
                Event.event_date.asc(),
                Event.start_time.asc()
            )
            .paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        )

    @staticmethod
    def has_bookings(event_id):
        return (
            db.session.query(Booking.id)
            .filter(
                Booking.event_id == event_id
            )
            .first()
            is not None
        )

    @staticmethod
    def update(event, **kwargs):
        for field, value in kwargs.items():
            if hasattr(event, field):
                setattr(event, field, value)

        db.session.flush()

        return event

    @staticmethod
    def delete(event):
        db.session.delete(event)
        db.session.flush()