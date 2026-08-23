from datetime import date, time
from decimal import Decimal

import pytest

from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.category import Category
from app.models.venue import Venue
from app.models.event import Event
from app.models.seat import Seat


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

        role = Role(
            name="CUSTOMER",
            description="Customer"
        )

        category = Category(
            name="Seat API Category",
            description="Seat API test category",
            is_active=True
        )

        venue = Venue(
            name="Seat API Venue",
            address="Test Address",
            city="Test City",
            capacity=10
        )

        db.session.add(role)
        db.session.add(category)
        db.session.add(venue)

        db.session.flush()

        published_event = Event(
            category_id=category.id,
            venue_id=venue.id,
            name="Seat API Event",
            description="Seat API test event",
            event_date=date(2026, 12, 10),
            start_time=time(18, 0),
            end_time=time(20, 0),
            status="PUBLISHED"
        )

        draft_event = Event(
            category_id=category.id,
            venue_id=venue.id,
            name="Seat API Draft Event",
            description="Draft event",
            event_date=date(2026, 12, 11),
            start_time=time(18, 0),
            end_time=time(20, 0),
            status="DRAFT"
        )

        db.session.add(published_event)
        db.session.add(draft_event)

        db.session.flush()

        seats = [
            Seat(
                venue_id=venue.id,
                seat_number="R1-S1",
                row_number=1,
                seat_type="VIP",
                price=Decimal("1500.00"),
                is_active=True
            ),
            Seat(
                venue_id=venue.id,
                seat_number="R1-S2",
                row_number=1,
                seat_type="VIP",
                price=Decimal("1500.00"),
                is_active=True
            ),
            Seat(
                venue_id=venue.id,
                seat_number="R2-S1",
                row_number=2,
                seat_type="PREMIUM",
                price=Decimal("1000.00"),
                is_active=True
            ),
            Seat(
                venue_id=venue.id,
                seat_number="R2-S2",
                row_number=2,
                seat_type="REGULAR",
                price=Decimal("500.00"),
                is_active=False
            )
        ]

        db.session.add_all(seats)

        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_available_seats(
    client,
    app
):

    with app.app_context():

        event = Event.query.filter_by(
            name="Seat API Event"
        ).first()

        event_id = event.id

    response = client.get(
        f"/api/v1/events/{event_id}/seats"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert (
        data["data"]["event_id"]
        == event_id
    )

    assert (
        data["data"]["event_name"]
        == "Seat API Event"
    )

    assert (
        data["data"]["total_seats"]
        == 3
    )

    assert (
        data["data"]["available_seats"]
        == 3
    )

    assert len(
        data["data"]["seats"]
    ) == 3


def test_seat_information_is_returned(
    client,
    app
):

    with app.app_context():

        event = Event.query.filter_by(
            name="Seat API Event"
        ).first()

        event_id = event.id

    response = client.get(
        f"/api/v1/events/{event_id}/seats"
    )

    data = response.get_json()

    seats = data["data"]["seats"]

    first_seat = seats[0]

    assert first_seat["seat_number"] == "R1-S1"
    assert first_seat["row_number"] == 1
    assert first_seat["seat_type"] == "VIP"
    assert first_seat["price"] == 1500.0


def test_inactive_seats_are_not_returned(
    client,
    app
):

    with app.app_context():

        event = Event.query.filter_by(
            name="Seat API Event"
        ).first()

        event_id = event.id

    response = client.get(
        f"/api/v1/events/{event_id}/seats"
    )

    data = response.get_json()

    seat_numbers = [
        seat["seat_number"]
        for seat in data["data"]["seats"]
    ]

    assert "R2-S2" not in seat_numbers


def test_unknown_event_returns_404(client):

    response = client.get(
        "/api/v1/events/999999/seats"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"

    assert (
        data["message"]
        == "Event not found"
    )


def test_draft_event_returns_404(
    client,
    app
):

    with app.app_context():

        event = Event.query.filter_by(
            name="Seat API Draft Event"
        ).first()

        event_id = event.id

    response = client.get(
        f"/api/v1/events/{event_id}/seats"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"

    assert (
        data["message"]
        == "Event not found"
    )