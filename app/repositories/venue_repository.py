from app.extensions import db
from app.models.venue import Venue
from app.models.event import Event
from app.models.seat import Seat


class VenueRepository:

    @staticmethod
    def create(
        name,
        address,
        city,
        capacity,
        description=None
    ):
        venue = Venue(
            name=name,
            address=address,
            city=city,
            capacity=capacity,
            description=description
        )

        db.session.add(venue)
        db.session.flush()

        return venue

    @staticmethod
    def get_by_id(venue_id):
        return db.session.get(Venue, venue_id)

    @staticmethod
    def get_all():
        return Venue.query.order_by(
            Venue.name.asc()
        ).all()

    @staticmethod
    def get_by_city(city):
        return (
            Venue.query
            .filter(Venue.city == city)
            .order_by(Venue.name.asc())
            .all()
        )

    @staticmethod
    def has_events(venue_id):
        return (
            db.session.query(Event.id)
            .filter(
                Event.venue_id == venue_id
            )
            .first()
            is not None
        )

    @staticmethod
    def has_seats(venue_id):
        return (
            db.session.query(Seat.id)
            .filter(
                Seat.venue_id == venue_id
            )
            .first()
            is not None
        )

    @staticmethod
    def update(venue, **kwargs):
        for field, value in kwargs.items():
            if hasattr(venue, field):
                setattr(venue, field, value)

        db.session.flush()

        return venue

    @staticmethod
    def delete(venue):
        db.session.delete(venue)
        db.session.flush()