from app.repositories.category_repository import CategoryRepository
from app.repositories.event_repository import EventRepository
from app.repositories.venue_repository import VenueRepository


class EventService:

    ALLOWED_STATUSES = {
        "DRAFT",
        "PUBLISHED",
        "CANCELLED",
        "COMPLETED"
    }

    @staticmethod
    def create_event(
        category_id,
        venue_id,
        name,
        description,
        event_date,
        start_time,
        end_time,
        status="DRAFT"
    ):
        category = CategoryRepository.get_by_id(category_id)

        if not category:
            raise ValueError("Category not found")

        venue = VenueRepository.get_by_id(venue_id)

        if not venue:
            raise ValueError("Venue not found")

        if status not in EventService.ALLOWED_STATUSES:
            raise ValueError("Invalid event status")

        if end_time <= start_time:
            raise ValueError(
                "Event end time must be after start time"
            )

        return EventRepository.create(
            category_id=category_id,
            venue_id=venue_id,
            name=name,
            description=description,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            status=status
        )

    @staticmethod
    def get_event(event_id):
        event = EventRepository.get_by_id(event_id)

        if not event:
            raise ValueError("Event not found")

        return event

    @staticmethod
    def get_events():
        return EventRepository.get_all()

    @staticmethod
    def search_events(
        keyword=None,
        category_id=None,
        venue_id=None,
        event_date=None,
        status=None,
        page=1,
        per_page=10
    ):
        return EventRepository.search(
            keyword=keyword,
            category_id=category_id,
            venue_id=venue_id,
            event_date=event_date,
            status=status,
            page=page,
            per_page=per_page
        )

    @staticmethod
    def update_event(event_id, **kwargs):
        event = EventService.get_event(event_id)

        if "status" in kwargs:
            if kwargs["status"] not in EventService.ALLOWED_STATUSES:
                raise ValueError("Invalid event status")

        if (
            "start_time" in kwargs
            and "end_time" in kwargs
            and kwargs["end_time"] <= kwargs["start_time"]
        ):
            raise ValueError(
                "Event end time must be after start time"
            )

        if "category_id" in kwargs:
            category = CategoryRepository.get_by_id(
                kwargs["category_id"]
            )

            if not category:
                raise ValueError("Category not found")

        if "venue_id" in kwargs:
            venue = VenueRepository.get_by_id(
                kwargs["venue_id"]
            )

            if not venue:
                raise ValueError("Venue not found")

        return EventRepository.update(
            event,
            **kwargs
        )

    @staticmethod
    def delete_event(event_id):
        event = EventService.get_by_id(event_id)

        EventRepository.delete(event)