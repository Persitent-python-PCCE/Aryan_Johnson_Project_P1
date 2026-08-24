from app.repositories.venue_repository import VenueRepository


class VenueService:

    @staticmethod
    def create_venue(
        name,
        address,
        city,
        capacity,
        description=None
    ):
        if capacity <= 0:
            raise ValueError(
                "Venue capacity must be greater than zero"
            )

        return VenueRepository.create(
            name=name,
            address=address,
            city=city,
            capacity=capacity,
            description=description
        )

    @staticmethod
    def get_venue(venue_id):
        venue = VenueRepository.get_by_id(venue_id)

        if not venue:
            raise ValueError("Venue not found")

        return venue

    @staticmethod
    def get_venues():
        return VenueRepository.get_all()

    @staticmethod
    def get_venues_by_city(city):
        return VenueRepository.get_by_city(city)

    @staticmethod
    def update_venue(venue_id, **kwargs):
        venue = VenueService.get_venue(venue_id)

        if "capacity" in kwargs and kwargs["capacity"] <= 0:
            raise ValueError(
                "Venue capacity must be greater than zero"
            )

        return VenueRepository.update(
            venue,
            **kwargs
        )

    @staticmethod
    def delete_venue(venue_id):
        venue = VenueService.get_venue(venue_id)

        VenueRepository.delete(venue)

    @staticmethod
    def delete_venue(venue_id):
        venue = VenueRepository.get_by_id(venue_id)

        if not venue:
            raise ValueError("Venue not found")

        if VenueRepository.has_events(venue_id):
            raise ValueError(
                "Cannot delete this venue because events are using it."
            )

        if VenueRepository.has_seats(venue_id):
            raise ValueError(
                "Cannot delete this venue because seats are configured for it."
            )

        VenueRepository.delete(venue)

        return venue