import os

from app.repositories.category_repository import CategoryRepository
from app.repositories.event_repository import EventRepository
from app.repositories.venue_repository import VenueRepository
from app.repositories.event_poster_repository import EventPosterRepository
from app.services.file_service import FileService

from app.extensions import db

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
        category = CategoryRepository.get_by_id(
            category_id
        )

        if not category:
            raise ValueError(
                "Category not found"
            )

        venue = VenueRepository.get_by_id(
            venue_id
        )

        if not venue:
            raise ValueError(
                "Venue not found"
            )

        if status not in EventService.VALID_STATUSES:
            raise ValueError(
                "Invalid event status"
            )

        if end_time <= start_time:
            raise ValueError(
                "Event end time must be after start time"
            )

        if not name or not name.strip():
            raise ValueError(
                "Event name is required"
            )

        event = EventRepository.create(
            category_id=category_id,
            venue_id=venue_id,
            name=name.strip(),
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
    def update_event(
        event_id,
        category_id,
        venue_id,
        name,
        description,
        event_date,
        start_time,
        end_time,
        status
    ):
        event = EventService.get_event(
            event_id
        )

        category = CategoryRepository.get_by_id(
            category_id
        )

        if not category:
            raise ValueError(
                "Category not found"
            )

        venue = VenueRepository.get_by_id(
            venue_id
        )

        if not venue:
            raise ValueError(
                "Venue not found"
            )

        if status not in EventService.VALID_STATUSES:
            raise ValueError(
                "Invalid event status"
            )

        if end_time <= start_time:
            raise ValueError(
                "Event end time must be after start time"
            )

        if not name or not name.strip():
            raise ValueError(
                "Event name is required"
            )

        EventRepository.update(
            event,
            category_id=category_id,
            venue_id=venue_id,
            name=name.strip(),
            description=description,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            status=status
        )

        return event

    @staticmethod
    def change_status(
        event_id,
        status
    ):
        event = EventService.get_event(
            event_id
        )

        if status not in EventService.VALID_STATUSES:
            raise ValueError(
                "Invalid event status"
            )

        event = EventRepository.update(
            event,
            status=status
        )

        return event

    @staticmethod
    def delete_event(event_id):
        event = EventRepository.get_by_id(event_id)

        if not event:
            raise ValueError("Event not found")

        if EventRepository.has_bookings(event_id):
            raise ValueError(
                "Cannot delete this event because bookings already exist."
            )

        posters = EventPosterRepository.get_by_event(
            event_id
        )

        for poster in posters:

            if poster.file_path:
                FileService.delete_file(
                    poster.file_path
                )

            db.session.delete(poster)

        EventRepository.delete(event)

        return event