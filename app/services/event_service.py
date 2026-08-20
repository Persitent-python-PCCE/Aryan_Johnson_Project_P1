from app.repositories.category_repository import CategoryRepository
from app.repositories.event_repository import EventRepository
from app.repositories.venue_repository import VenueRepository


class EventService:

    VALID_STATUSES = {
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
        # Validate category
        category = CategoryRepository.get_by_id(
            category_id
        )

        if not category:
            raise ValueError(
                "Category not found"
            )

        # Validate venue
        venue = VenueRepository.get_by_id(
            venue_id
        )

        if not venue:
            raise ValueError(
                "Venue not found"
            )

        # Validate event status
        if status not in EventService.VALID_STATUSES:
            raise ValueError(
                "Invalid event status"
            )

        # Validate event time range
        if end_time <= start_time:
            raise ValueError(
                "Event end time must be after start time"
            )

        event = EventRepository.create(
            category_id=category_id,
            venue_id=venue_id,
            name=name,
            description=description,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            status=status
        )

        return event

    @staticmethod
    def get_event(event_id):
        event = EventRepository.get_by_id(
            event_id
        )

        if not event:
            raise ValueError(
                "Event not found"
            )

        return event

    @staticmethod
    def search_events(
        keyword=None,
        page=1,
        per_page=10
    ):
        return EventRepository.search(
            keyword=keyword,
            page=page,
            per_page=per_page
        )