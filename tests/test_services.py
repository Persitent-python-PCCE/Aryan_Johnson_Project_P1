from datetime import date, time

import pytest

from app import create_app
from app.extensions import db
from app.services.category_service import CategoryService
from app.services.venue_service import VenueService
from app.services.event_service import EventService
from app.services.seat_service import SeatService
from app.services.booking_service import BookingService
from app.repositories.booking_item_repository import (BookingItemRepository,)
from app.repositories.user_repository import UserRepository
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.services.file_service import FileService
from app.services.booking_service import BookingRepository


from app.models.role import Role
from app.models.user import User


@pytest.fixture
def app():
    app = create_app()

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session


# ---------------------------------------------------------------------------
# CategoryService
# ---------------------------------------------------------------------------

def test_category_service_create_and_get(session):
    category = CategoryService.create_category(
        name="Concert",
        description="Live music events"
    )

    session.commit()

    result = CategoryService.get_category(category.id)

    assert result is not None
    assert result.name == "Concert"
    assert result.description == "Live music events"


def test_category_service_rejects_duplicate_name(session):
    CategoryService.create_category(
        name="Concert"
    )

    session.commit()

    with pytest.raises(ValueError, match="Category already exists"):
        CategoryService.create_category(
            name="Concert"
        )


def test_category_service_get_missing_category(session):
    with pytest.raises(ValueError, match="Category not found"):
        CategoryService.get_category(999)


# ---------------------------------------------------------------------------
# VenueService
# ---------------------------------------------------------------------------

def test_venue_service_create_and_get(session):
    venue = VenueService.create_venue(
        name="City Arena",
        address="Main Street",
        city="Bangalore",
        capacity=10000,
        description="Large event venue"
    )

    session.commit()

    result = VenueService.get_venue(venue.id)

    assert result is not None
    assert result.name == "City Arena"
    assert result.city == "Bangalore"
    assert result.capacity == 10000


def test_venue_service_rejects_invalid_capacity(session):
    with pytest.raises(
        ValueError,
        match="Venue capacity must be greater than zero"
    ):
        VenueService.create_venue(
            name="Invalid Venue",
            address="Main Street",
            city="Bangalore",
            capacity=0
        )


def test_venue_service_get_by_city(session):
    VenueService.create_venue(
        name="Bangalore Arena",
        address="MG Road",
        city="Bangalore",
        capacity=5000
    )

    VenueService.create_venue(
        name="Mumbai Arena",
        address="Marine Drive",
        city="Mumbai",
        capacity=7000
    )

    session.commit()

    venues = VenueService.get_venues_by_city("Bangalore")

    assert len(venues) == 1
    assert venues[0].name == "Bangalore Arena"


# ---------------------------------------------------------------------------
# EventService
# ---------------------------------------------------------------------------

def create_test_category_and_venue():
    category = CategoryService.create_category(
        name="Concert"
    )

    venue = VenueService.create_venue(
        name="City Arena",
        address="Main Street",
        city="Bangalore",
        capacity=10000
    )

    return category, venue


def test_event_service_create_and_get(session):
    category, venue = create_test_category_and_venue()

    session.flush()

    event = EventService.create_event(
        category_id=category.id,
        venue_id=venue.id,
        name="Rock Night",
        description="Live concert",
        event_date=date(2026, 12, 10),
        start_time=time(18, 0),
        end_time=time(22, 0)
    )

    session.commit()

    result = EventService.get_event(event.id)

    assert result is not None
    assert result.name == "Rock Night"
    assert result.category_id == category.id
    assert result.venue_id == venue.id
    assert result.status == "DRAFT"


def test_event_service_rejects_invalid_category(session):
    venue = VenueService.create_venue(
        name="City Arena",
        address="Main Street",
        city="Bangalore",
        capacity=10000
    )

    session.flush()

    with pytest.raises(ValueError, match="Category not found"):
        EventService.create_event(
            category_id=999,
            venue_id=venue.id,
            name="Rock Night",
            description="Live concert",
            event_date=date(2026, 12, 10),
            start_time=time(18, 0),
            end_time=time(22, 0)
        )


def test_event_service_rejects_invalid_venue(session):
    category = CategoryService.create_category(
        name="Concert"
    )

    session.flush()

    with pytest.raises(ValueError, match="Venue not found"):
        EventService.create_event(
            category_id=category.id,
            venue_id=999,
            name="Rock Night",
            description="Live concert",
            event_date=date(2026, 12, 10),
            start_time=time(18, 0),
            end_time=time(22, 0)
        )


def test_event_service_rejects_invalid_status(session):
    category, venue = create_test_category_and_venue()

    session.flush()

    with pytest.raises(ValueError, match="Invalid event status"):
        EventService.create_event(
            category_id=category.id,
            venue_id=venue.id,
            name="Rock Night",
            description="Live concert",
            event_date=date(2026, 12, 10),
            start_time=time(18, 0),
            end_time=time(22, 0),
            status="INVALID"
        )


def test_event_service_rejects_invalid_time_range(session):
    category, venue = create_test_category_and_venue()

    session.flush()

    with pytest.raises(
        ValueError,
        match="Event end time must be after start time"
    ):
        EventService.create_event(
            category_id=category.id,
            venue_id=venue.id,
            name="Rock Night",
            description="Live concert",
            event_date=date(2026, 12, 10),
            start_time=time(22, 0),
            end_time=time(18, 0)
        )


def test_event_service_search(session):
    category, venue = create_test_category_and_venue()

    session.flush()

    EventService.create_event(
        category_id=category.id,
        venue_id=venue.id,
        name="Rock Night",
        description="Live rock concert",
        event_date=date(2026, 12, 10),
        start_time=time(18, 0),
        end_time=time(22, 0),
        status="PUBLISHED"
    )

    EventService.create_event(
        category_id=category.id,
        venue_id=venue.id,
        name="Jazz Evening",
        description="Live jazz concert",
        event_date=date(2026, 12, 11),
        start_time=time(18, 0),
        end_time=time(21, 0),
        status="PUBLISHED"
    )

    session.commit()

    result = EventService.search_events(
        keyword="Rock",
        page=1,
        per_page=10
    )

    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].name == "Rock Night"


def test_seat_service_create_and_get(session):
    venue = VenueService.create_venue(
        name="Seat Test Arena",
        address="Main Street",
        city="Bangalore",
        capacity=100
    )

    session.flush()

    seat = SeatService.create_seat(
        venue_id=venue.id,
        seat_number="A1",
        row_number=1,
        seat_type="REGULAR",
        price=500.00
    )

    session.commit()

    result = SeatService.get_seat(seat.id)

    assert result is not None
    assert result.seat_number == "A1"
    assert result.venue_id == venue.id
    assert float(result.price) == 500.00


def test_seat_service_rejects_invalid_venue(session):
    with pytest.raises(ValueError, match="Venue not found"):
        SeatService.create_seat(
            venue_id=999,
            seat_number="A1",
            row_number=1,
            seat_type="REGULAR",
            price=500.00
        )


def test_seat_service_rejects_invalid_row(session):
    venue = VenueService.create_venue(
        name="Row Test Arena",
        address="Main Street",
        city="Bangalore",
        capacity=100
    )

    session.flush()

    with pytest.raises(
        ValueError,
        match="Row number must be greater than zero"
    ):
        SeatService.create_seat(
            venue_id=venue.id,
            seat_number="A1",
            row_number=0,
            seat_type="REGULAR",
            price=500.00
        )


def test_seat_service_rejects_negative_price(session):
    venue = VenueService.create_venue(
        name="Price Test Arena",
        address="Main Street",
        city="Bangalore",
        capacity=100
    )

    session.flush()

    with pytest.raises(
        ValueError,
        match="Seat price cannot be negative"
    ):
        SeatService.create_seat(
            venue_id=venue.id,
            seat_number="A1",
            row_number=1,
            seat_type="REGULAR",
            price=-100.00
        )


def test_seat_service_rejects_invalid_seat_type(session):
    venue = VenueService.create_venue(
        name="Type Test Arena",
        address="Main Street",
        city="Bangalore",
        capacity=100
    )

    session.flush()

    with pytest.raises(
        ValueError,
        match="Invalid seat type"
    ):
        SeatService.create_seat(
            venue_id=venue.id,
            seat_number="A1",
            row_number=1,
            seat_type="INVALID",
            price=500.00
        )


def test_seat_service_rejects_duplicate_seat_number(session):
    venue = VenueService.create_venue(
        name="Duplicate Test Arena",
        address="Main Street",
        city="Bangalore",
        capacity=100
    )

    session.flush()

    SeatService.create_seat(
        venue_id=venue.id,
        seat_number="A1",
        row_number=1,
        seat_type="REGULAR",
        price=500.00
    )

    session.flush()

    with pytest.raises(
        ValueError,
        match="Seat number already exists for this venue"
    ):
        SeatService.create_seat(
            venue_id=venue.id,
            seat_number="A1",
            row_number=1,
            seat_type="REGULAR",
            price=500.00
        )


def create_booking_test_data(session):
    role = Role(
        name="CUSTOMER",
        description="Test customer"
    )

    session.add(role)
    session.flush()

    user = User(
        name="Booking User",
        email="booking-service@example.com",
        password_hash="hashed-password",
        role_id=role.id
    )

    session.add(user)

    category = CategoryService.create_category(
        name="Booking Concert"
    )

    venue = VenueService.create_venue(
        name="Booking Arena",
        address="Main Street",
        city="Bangalore",
        capacity=100
    )

    session.flush()

    event = EventService.create_event(
        category_id=category.id,
        venue_id=venue.id,
        name="Booking Concert",
        description="Booking service test event",
        event_date=date(2026, 12, 30),
        start_time=time(18, 0),
        end_time=time(22, 0),
        status="PUBLISHED"
    )

    session.flush()

    seat_a1 = SeatService.create_seat(
        venue_id=venue.id,
        seat_number="A1",
        row_number=1,
        seat_type="REGULAR",
        price=500.00
    )

    seat_a2 = SeatService.create_seat(
        venue_id=venue.id,
        seat_number="A2",
        row_number=1,
        seat_type="PREMIUM",
        price=750.00
    )

    session.commit()

    return user, event, seat_a1, seat_a2


def test_booking_service_create_booking(session):
    user, event, seat_a1, seat_a2 = create_booking_test_data(
        session
    )

    booking = BookingService.create_booking(
        user_id=user.id,
        event_id=event.id,
        seat_ids=[seat_a1.id, seat_a2.id]
    )

    assert booking is not None
    assert booking.user_id == user.id
    assert booking.event_id == event.id
    assert booking.status == "CONFIRMED"
    assert booking.booking_reference.startswith("BK-")

    assert float(booking.total_amount) == 1250.00



def test_booking_service_creates_booking_items(session):
    user, event, seat_a1, seat_a2 = create_booking_test_data(
        session
    )

    booking = BookingService.create_booking(
        user_id=user.id,
        event_id=event.id,
        seat_ids=[seat_a1.id, seat_a2.id]
    )

    items = BookingItemRepository.get_by_booking(
        booking.id
    )

    assert len(items) == 2

    prices = {
        item.seat_id: float(item.price)
        for item in items
    }

    assert prices[seat_a1.id] == 500.00
    assert prices[seat_a2.id] == 750.00


def test_booking_service_rejects_invalid_event(session):
    user, _, seat_a1, _ = create_booking_test_data(
        session
    )

    with pytest.raises(
        ValueError,
        match="Event not found"
    ):
        BookingService.create_booking(
            user_id=user.id,
            event_id=999,
            seat_ids=[seat_a1.id]
        )


def test_booking_service_rejects_invalid_seat(session):
    user, event, _, _ = create_booking_test_data(
        session
    )

    with pytest.raises(
        ValueError,
        match="Seat 999 not found"
    ):
        BookingService.create_booking(
            user_id=user.id,
            event_id=event.id,
            seat_ids=[999]
        )


def test_booking_service_rejects_seat_from_another_venue(session):
    user, event, _, _ = create_booking_test_data(
        session
    )

    other_venue = VenueService.create_venue(
        name="Other Arena",
        address="Other Street",
        city="Bangalore",
        capacity=100
    )

    session.flush()

    other_seat = SeatService.create_seat(
        venue_id=other_venue.id,
        seat_number="A1",
        row_number=1,
        seat_type="REGULAR",
        price=500.00
    )

    session.commit()

    with pytest.raises(
        ValueError,
        match="does not belong to the event venue"
    ):
        BookingService.create_booking(
            user_id=user.id,
            event_id=event.id,
            seat_ids=[other_seat.id]
        )


def test_booking_service_rejects_cancelled_event(session):
    user, event, seat_a1, _ = create_booking_test_data(
        session
    )

    event.status = "CANCELLED"
    session.commit()

    with pytest.raises(
        ValueError,
        match="Event is not available for booking"
    ):
        BookingService.create_booking(
            user_id=user.id,
            event_id=event.id,
            seat_ids=[seat_a1.id]
        )


def test_booking_service_rejects_already_booked_seat(session):
    user, event, seat_a1, seat_a2 = create_booking_test_data(
        session
    )

    BookingService.create_booking(
        user_id=user.id,
        event_id=event.id,
        seat_ids=[seat_a1.id]
    )

    with pytest.raises(
        ValueError,
        match=f"Seat {seat_a1.id} is already booked"
    ):
        BookingService.create_booking(
            user_id=user.id,
            event_id=event.id,
            seat_ids=[seat_a1.id]
        )


def test_booking_service_get_user_bookings(session):
    user, event, seat_a1, seat_a2 = create_booking_test_data(
        session
    )

    BookingService.create_booking(
        user_id=user.id,
        event_id=event.id,
        seat_ids=[seat_a1.id]
    )

    bookings = BookingService.get_user_bookings(
        user.id
    )

    assert len(bookings) == 1
    assert bookings[0].user_id == user.id


def test_booking_service_cancel_booking(session):
    user, event, seat_a1, _ = create_booking_test_data(
        session
    )

    booking = BookingService.create_booking(
        user_id=user.id,
        event_id=event.id,
        seat_ids=[seat_a1.id]
    )

    cancelled_booking = BookingService.cancel_booking(
        booking.id
    )

    assert cancelled_booking.status == "CANCELLED"
    assert cancelled_booking.cancelled_at is not None


def test_role_service_create_and_get(session):
    role = RoleService.create_role(
        name="ADMIN",
        description="System administrator"
    )

    session.commit()

    result = RoleService.get_role(role.id)

    assert result.name == "ADMIN"


def test_role_service_rejects_invalid_role(session):
    with pytest.raises(
        ValueError,
        match="Invalid role"
    ):
        RoleService.create_role(
            name="MANAGER"
        )


def test_role_service_rejects_duplicate_role(session):
    RoleService.create_role(
        name="ADMIN"
    )

    session.commit()

    with pytest.raises(
        ValueError,
        match="Role already exists"
    ):
        RoleService.create_role(
            name="ADMIN"
        )

def test_role_service_rejects_duplicate_role(session):
    RoleService.create_role(
        name="ADMIN"
    )

    session.commit()

    with pytest.raises(
        ValueError,
        match="Role already exists"
    ):
        RoleService.create_role(
            name="ADMIN"
        )


def test_user_service_get_user(session):
    role = RoleService.create_role(
        name="CUSTOMER"
    )

    session.flush()

    user = UserRepository.create(
        name="Service User",
        email="service@example.com",
        password_hash="hashed-password",
        role_id=role.id
    )

    session.commit()

    result = UserService.get_user(user.id)

    assert result.email == "service@example.com"


def test_user_service_rejects_missing_user(session):
    with pytest.raises(
        ValueError,
        match="User not found"
    ):
        UserService.get_user(999)


def test_user_service_deactivate_user(session):
    role = RoleService.create_role(
        name="CUSTOMER"
    )

    session.flush()

    user = UserRepository.create(
        name="Active User",
        email="active@example.com",
        password_hash="hashed-password",
        role_id=role.id
    )

    session.commit()

    UserService.deactivate_user(user.id)

    session.commit()

    result = UserService.get_user(user.id)

    assert result.is_active is False


def test_file_service_accepts_valid_poster(session):
    filename = FileService.validate_poster(
        "concert.jpg",
        1024,
        "image/jpeg"
    )

    assert filename == "concert.jpg"


def test_file_service_accepts_valid_png_poster(session):
    filename = FileService.validate_poster(
        "concert.png",
        2048,
        "image/png"
    )

    assert filename == "concert.png"


def test_file_service_rejects_invalid_poster_extension(session):
    with pytest.raises(
        ValueError,
        match="Unsupported file extension"
    ):
        FileService.validate_poster(
            "concert.exe",
            1024,
            "application/octet-stream"
        )


def test_file_service_rejects_invalid_poster_mime(session):
    with pytest.raises(
        ValueError,
        match="Unsupported MIME type"
    ):
        FileService.validate_poster(
            "concert.jpg",
            1024,
            "application/pdf"
        )


def test_file_service_rejects_large_file(session):
    with pytest.raises(
        ValueError,
        match="File size exceeds maximum limit"
    ):
        FileService.validate_poster(
            "concert.jpg",
            6 * 1024 * 1024,
            "image/jpeg"
        )


def test_file_service_rejects_empty_file(session):
    with pytest.raises(
        ValueError,
        match="File cannot be empty"
    ):
        FileService.validate_poster(
            "concert.jpg",
            0,
            "image/jpeg"
        )


def test_file_service_accepts_pdf_document(session):
    filename = FileService.validate_document(
        "identity.pdf",
        1024,
        "application/pdf"
    )

    assert filename == "identity.pdf"


def test_file_service_rejects_invalid_document_extension(session):
    with pytest.raises(
        ValueError,
        match="Unsupported file extension"
    ):
        FileService.validate_document(
            "identity.exe",
            1024,
            "application/octet-stream"
        )


def test_file_service_rejects_invalid_document_mime(session):
    with pytest.raises(
        ValueError,
        match="Unsupported MIME type"
    ):
        FileService.validate_document(
            "identity.pdf",
            1024,
            "image/gif"
        )


def test_file_service_rejects_missing_document_type(session):
    role = Role(
        name="CUSTOMER",
        description="Test customer"
    )

    session.add(role)
    session.flush()

    user = UserRepository.create(
        name="Document Test User",
        email="document-service@example.com",
        password_hash="hashed-password",
        role_id=role.id
    )

    session.commit()

    with pytest.raises(
        ValueError,
        match="Document type is required"
    ):
        FileService.save_document(
            user_id=user.id,
            document_type="",
            filename="identity.pdf",
            file_size=1024,
            mime_type="application/pdf",
            file_object=None
        )


def test_file_service_generates_unique_filename(session):
    filename_one = FileService._generate_stored_filename(
        "jpg"
    )

    filename_two = FileService._generate_stored_filename(
        "jpg"
    )

    assert filename_one != filename_two
    assert filename_one.endswith(".jpg")
    assert filename_two.endswith(".jpg")


def test_booking_service_books_multiple_seats_atomically(
    session
):
    user, event, seat_a1, seat_a2 = (
        create_booking_test_data(session)
    )

    booking = BookingService.create_booking(
        user_id=user.id,
        event_id=event.id,
        seat_ids=[
            seat_a1.id,
            seat_a2.id
        ]
    )

    assert booking is not None
    assert booking.status == "CONFIRMED"

    items = BookingItemRepository.get_by_booking(
        booking.id
    )

    assert len(items) == 2


def test_booking_service_rolls_back_on_failure(
    session,
    monkeypatch
):
    user, event, seat_a1, seat_a2 = (
        create_booking_test_data(session)
    )

    original_create = (
        BookingItemRepository.create
    )

    call_count = {"value": 0}

    def failing_create(*args, **kwargs):
        call_count["value"] += 1

        if call_count["value"] == 2:
            raise RuntimeError(
                "Simulated booking item failure"
            )

        return original_create(
            *args,
            **kwargs
        )

    monkeypatch.setattr(
        BookingItemRepository,
        "create",
        failing_create
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated booking item failure"
    ):
        BookingService.create_booking(
            user_id=user.id,
            event_id=event.id,
            seat_ids=[
                seat_a1.id,
                seat_a2.id
            ]
        )

    bookings = BookingRepository.get_by_user(
        user.id
    )

    assert len(bookings) == 0