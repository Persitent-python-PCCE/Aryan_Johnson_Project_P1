from datetime import date, time

import pytest

from app import create_app
from app.extensions import db
from app.models import Category, Venue, Event, Seat
from app.repositories.category_repository import CategoryRepository
from app.repositories.venue_repository import VenueRepository
from app.repositories.event_repository import EventRepository
from app.repositories.seat_repository import SeatRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.booking_item_repository import BookingItemRepository
from app.repositories.user_document_repository import UserDocumentRepository
from app.repositories.event_poster_repository import EventPosterRepository
from app.repositories.user_repository import UserRepository

from app.models.role import Role
from app.models.user import User


@pytest.fixture
def app():
    app = create_app(
        test_config={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret"
        }
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


def test_category_repository_create_and_get(session):
    category = CategoryRepository.create(
        name="Concert",
        description="Live music events"
    )

    session.commit()

    result = CategoryRepository.get_by_id(category.id)

    assert result is not None
    assert result.name == "Concert"
    assert result.description == "Live music events"


def test_venue_repository_create_and_get(session):
    venue = VenueRepository.create(
        name="City Arena",
        address="Main Street",
        city="Bangalore",
        capacity=10000
    )

    session.commit()

    result = VenueRepository.get_by_id(venue.id)

    assert result is not None
    assert result.name == "City Arena"
    assert result.city == "Bangalore"
    assert result.capacity == 10000


def test_event_repository_create_and_get(session):
    category = CategoryRepository.create(
        name="Concert"
    )

    venue = VenueRepository.create(
        name="City Arena",
        address="Main Street",
        city="Bangalore",
        capacity=10000
    )

    session.commit()

    event = EventRepository.create(
        category_id=category.id,
        venue_id=venue.id,
        name="Rock Night",
        description="Live concert",
        event_date=date(2026, 12, 10),
        start_time=time(18, 0),
        end_time=time(22, 0)
    )

    session.commit()

    result = EventRepository.get_by_id(event.id)

    assert result is not None
    assert result.name == "Rock Night"
    assert result.category_id == category.id
    assert result.venue_id == venue.id


def test_seat_repository_create_and_get_by_venue(session):
    venue = VenueRepository.create(
        name="City Arena",
        address="Main Street",
        city="Bangalore",
        capacity=100
    )

    session.commit()

    seat = SeatRepository.create(
        venue_id=venue.id,
        seat_number="A1",
        row_number=1,
        seat_type="REGULAR",
        price=500.00
    )

    session.commit()

    seats = SeatRepository.get_by_venue(venue.id)

    assert len(seats) == 1
    assert seats[0].seat_number == "A1"
    assert seats[0].venue_id == venue.id


def test_booking_repository_create_and_get(session):
    role = Role(
        name="CUSTOMER",
        description="Test customer"
    )

    session.add(role)
    session.flush()

    user = User(
        name="Test User",
        email="test@example.com",
        password_hash="hashed-password",
        role_id=role.id
    )

    session.add(user)

    category = CategoryRepository.create(
        name="Concert"
    )

    venue = VenueRepository.create(
        name="City Arena",
        address="Main Street",
        city="Bangalore",
        capacity=100
    )

    session.flush()

    event = EventRepository.create(
        category_id=category.id,
        venue_id=venue.id,
        name="Rock Night",
        description="Live concert",
        event_date=date(2026, 12, 10),
        start_time=time(18, 0),
        end_time=time(22, 0)
    )

    session.flush()

    booking = BookingRepository.create(
        user_id=user.id,
        event_id=event.id,
        booking_reference="BK-TEST-001",
        total_amount=1000.00
    )

    session.commit()

    result = BookingRepository.get_by_id(booking.id)

    assert result is not None
    assert result.booking_reference == "BK-TEST-001"
    assert result.user_id == user.id
    assert result.event_id == event.id
    assert float(result.total_amount) == 1000.00


def test_booking_item_repository_create_and_get_by_booking(session):
    role = Role(
        name="CUSTOMER",
        description="Test customer"
    )

    session.add(role)
    session.flush()

    user = User(
        name="Test User",
        email="booking-item@example.com",
        password_hash="hashed-password",
        role_id=role.id
    )

    session.add(user)

    category = CategoryRepository.create(
        name="Concert"
    )

    venue = VenueRepository.create(
        name="City Arena",
        address="Main Street",
        city="Bangalore",
        capacity=100
    )

    session.flush()

    event = EventRepository.create(
        category_id=category.id,
        venue_id=venue.id,
        name="Rock Night",
        description="Live concert",
        event_date=date(2026, 12, 10),
        start_time=time(18, 0),
        end_time=time(22, 0)
    )

    session.flush()

    seat = SeatRepository.create(
        venue_id=venue.id,
        seat_number="A1",
        row_number=1,
        seat_type="REGULAR",
        price=500.00
    )

    session.flush()

    booking = BookingRepository.create(
        user_id=user.id,
        event_id=event.id,
        booking_reference="BK-TEST-002",
        total_amount=500.00
    )

    session.flush()

    booking_item = BookingItemRepository.create(
        booking_id=booking.id,
        seat_id=seat.id,
        price=500.00
    )

    session.commit()

    items = BookingItemRepository.get_by_booking(
        booking.id
    )

    assert len(items) == 1
    assert items[0].id == booking_item.id
    assert items[0].seat_id == seat.id
    assert float(items[0].price) == 500.00

def test_user_document_repository_create_and_get_by_user(session):
    role = Role(
        name="CUSTOMER",
        description="Test customer"
    )

    session.add(role)
    session.flush()

    user = User(
        name="Document User",
        email="document@example.com",
        password_hash="hashed-password",
        role_id=role.id
    )

    session.add(user)
    session.flush()

    document = UserDocumentRepository.create(
        user_id=user.id,
        document_type="ID_PROOF",
        original_filename="passport.pdf",
        stored_filename="abc123_passport.pdf",
        file_path="private/documents/abc123_passport.pdf",
        file_size=2048,
        mime_type="application/pdf"
    )

    session.commit()

    result = UserDocumentRepository.get_by_id(document.id)

    assert result is not None
    assert result.user_id == user.id
    assert result.document_type == "ID_PROOF"
    assert result.stored_filename == "abc123_passport.pdf"

def test_event_poster_repository_create_and_get_by_event(session):
    category = CategoryRepository.create(
        name="Sports"
    )

    venue = VenueRepository.create(
        name="Sports Arena",
        address="Main Street",
        city="Bangalore",
        capacity=5000
    )

    session.flush()

    event = EventRepository.create(
        category_id=category.id,
        venue_id=venue.id,
        name="Football Final",
        description="Championship final",
        event_date=date(2026, 12, 20),
        start_time=time(18, 0),
        end_time=time(21, 0)
    )

    session.flush()

    poster = EventPosterRepository.create(
        event_id=event.id,
        original_filename="final.jpg",
        stored_filename="xyz789_final.jpg",
        file_path="public/posters/xyz789_final.jpg",
        file_size=4096,
        mime_type="image/jpeg"
    )

    session.commit()

    posters = EventPosterRepository.get_by_event(event.id)

    assert len(posters) == 1
    assert posters[0].id == poster.id
    assert posters[0].event_id == event.id
    assert posters[0].mime_type == "image/jpeg"


def test_seat_repository_get_available_for_event(session):
    role = Role(
        name="CUSTOMER",
        description="Test customer"
    )

    session.add(role)
    session.flush()

    user = User(
        name="Availability User",
        email="availability@example.com",
        password_hash="hashed-password",
        role_id=role.id
    )

    session.add(user)
    session.flush()

    category = CategoryRepository.create(
        name="Concert"
    )

    venue = VenueRepository.create(
        name="Availability Arena",
        address="Main Street",
        city="Bangalore",
        capacity=100
    )

    session.flush()

    event = EventRepository.create(
        category_id=category.id,
        venue_id=venue.id,
        name="Availability Test Event",
        description="Testing seat availability",
        event_date=date(2026, 12, 25),
        start_time=time(18, 0),
        end_time=time(21, 0)
    )

    session.flush()

    seat_a1 = SeatRepository.create(
        venue_id=venue.id,
        seat_number="A1",
        row_number=1,
        seat_type="REGULAR",
        price=500.00
    )

    seat_a2 = SeatRepository.create(
        venue_id=venue.id,
        seat_number="A2",
        row_number=1,
        seat_type="REGULAR",
        price=500.00
    )

    session.flush()

    # Initially both seats should be available.
    available_seats = SeatRepository.get_available_for_event(
        event.id
    )

    assert len(available_seats) == 2
    assert {seat.seat_number for seat in available_seats} == {
        "A1",
        "A2"
    }

    # Book A1.
    booking = BookingRepository.create(
        user_id=user.id,
        event_id=event.id,
        booking_reference="BK-AVAILABILITY-001",
        total_amount=500.00,
        status="CONFIRMED"
    )

    session.flush()

    BookingItemRepository.create(
        booking_id=booking.id,
        seat_id=seat_a1.id,
        price=500.00
    )

    session.commit()

    # A1 should now be unavailable, while A2 remains available.
    available_seats = SeatRepository.get_available_for_event(
        event.id
    )

    assert len(available_seats) == 1
    assert available_seats[0].seat_number == "A2"


def test_user_repository_create_and_get(session):
    role = Role(
        name="CUSTOMER",
        description="Test customer"
    )

    session.add(role)
    session.flush()

    user = UserRepository.create(
        name="Repository User",
        email="repository@example.com",
        password_hash="hashed-password",
        role_id=role.id
    )

    session.commit()

    result = UserRepository.get_by_id(user.id)

    assert result is not None
    assert result.name == "Repository User"
    assert result.email == "repository@example.com"
    assert result.role_id == role.id


def test_user_repository_get_by_email(session):
    role = Role(
        name="CUSTOMER",
        description="Test customer"
    )

    session.add(role)
    session.flush()

    UserRepository.create(
        name="Email User",
        email="email@example.com",
        password_hash="hashed-password",
        role_id=role.id
    )

    session.commit()

    result = UserRepository.get_by_email(
        "email@example.com"
    )

    assert result is not None
    assert result.name == "Email User"


def test_seat_repository_get_by_id_for_update(session):
    venue = VenueRepository.create(
        name="Lock Test Arena",
        address="Main Street",
        city="Bangalore",
        capacity=100
    )

    session.flush()

    seat = SeatRepository.create(
        venue_id=venue.id,
        seat_number="A1",
        row_number=1,
        seat_type="REGULAR",
        price=500.00
    )

    session.commit()

    result = SeatRepository.get_by_id_for_update(
        seat.id
    )

    assert result is not None
    assert result.id == seat.id
    assert result.seat_number == "A1"