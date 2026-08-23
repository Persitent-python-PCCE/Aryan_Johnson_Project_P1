from datetime import date, time
from decimal import Decimal

import pytest

from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.user import User
from app.models.category import Category
from app.models.venue import Venue
from app.models.event import Event
from app.models.seat import Seat
from app.services.auth_service import AuthService


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

        customer_role = Role(
            name="CUSTOMER",
            description="Customer"
        )

        admin_role = Role(
            name="ADMIN",
            description="Administrator"
        )

        category = Category(
            name="Booking API Category",
            description="Booking API test category",
            is_active=True
        )

        venue = Venue(
            name="Booking API Venue",
            address="Test Address",
            city="Test City",
            capacity=10
        )

        db.session.add(customer_role)
        db.session.add(admin_role)
        db.session.add(category)
        db.session.add(venue)

        db.session.flush()

        event = Event(
            category_id=category.id,
            venue_id=venue.id,
            name="Booking API Event",
            description="Booking API test event",
            event_date=date(2026, 12, 20),
            start_time=time(18, 0),
            end_time=time(20, 0),
            status="PUBLISHED"
        )

        db.session.add(event)

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
                seat_number="R1-S3",
                row_number=1,
                seat_type="PREMIUM",
                price=Decimal("1000.00"),
                is_active=True
            )
        ]

        db.session.add_all(seats)

        customer = AuthService.register(
            name="Booking Customer",
            email="booking@example.com",
            password="password123"
        )

        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(
    client,
    app
):

    with app.app_context():

        user = User.query.filter_by(
            email="booking@example.com"
        ).first()

        user_id = user.id

    with client.session_transaction() as session:

        session["user_id"] = user_id
        session["role"] = "CUSTOMER"

    return client


def get_event_and_seats(app):

    with app.app_context():

        event = Event.query.filter_by(
            name="Booking API Event"
        ).first()

        seats = (
            Seat.query
            .filter_by(
                venue_id=event.venue_id,
                is_active=True
            )
            .order_by(Seat.id.asc())
            .all()
        )

        return (
            event.id,
            [seat.id for seat in seats]
        )


def test_create_booking(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": seat_ids[:2]
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["status"] == "success"

    assert (
        data["message"]
        == "Booking created successfully"
    )

    booking = data["data"]

    assert booking["event"]["id"] == event_id

    assert (
        booking["status"]
        == "CONFIRMED"
    )

    assert (
        booking["total_amount"]
        == 3000.0
    )

    assert len(
        booking["seats"]
    ) == 2


def test_get_user_bookings(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    create_response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [seat_ids[0]]
        }
    )

    assert create_response.status_code == 201

    response = authenticated_client.get(
        "/api/v1/bookings"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert len(
        data["data"]
    ) == 1

    assert (
        data["data"][0]["status"]
        == "CONFIRMED"
    )


def test_get_booking_details(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    create_response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [seat_ids[0]]
        }
    )

    booking_id = (
        create_response
        .get_json()["data"]["id"]
    )

    response = authenticated_client.get(
        f"/api/v1/bookings/{booking_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert (
        data["data"]["id"]
        == booking_id
    )


def test_customer_cannot_view_another_customers_booking(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    # Customer 1 creates the booking.
    create_response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [seat_ids[0]]
        }
    )

    assert create_response.status_code == 201

    booking_id = (
        create_response
        .get_json()["data"]["id"]
    )

    # Create Customer 2.
    with app.app_context():

        second_customer = AuthService.register(
            name="Second Booking Customer",
            email="second-booking@example.com",
            password="password123"
        )

        db.session.commit()

        second_customer_id = second_customer.id

    # Authenticate as Customer 2.
    with authenticated_client.session_transaction() as session:
        session["user_id"] = second_customer_id
        session["role"] = "CUSTOMER"

    # Customer 2 attempts to access Customer 1's booking.
    response = authenticated_client.get(
        f"/api/v1/bookings/{booking_id}"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Booking not found"


def test_customer_cannot_cancel_another_customers_booking(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    # Customer 1 creates the booking.
    create_response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [seat_ids[0]]
        }
    )

    assert create_response.status_code == 201

    booking_id = (
        create_response
        .get_json()["data"]["id"]
    )

    # Create Customer 2.
    with app.app_context():

        second_customer = AuthService.register(
            name="Second Booking Customer",
            email="second-cancel@example.com",
            password="password123"
        )

        db.session.commit()

        second_customer_id = second_customer.id

    # Authenticate as Customer 2.
    with authenticated_client.session_transaction() as session:
        session["user_id"] = second_customer_id
        session["role"] = "CUSTOMER"

    # Customer 2 attempts to cancel Customer 1's booking.
    response = authenticated_client.post(
        f"/api/v1/bookings/{booking_id}/cancel"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Booking not found"

    # Verify the original booking is still confirmed.
    with app.app_context():

        from app.models.booking import Booking

        booking = db.session.get(
            Booking,
            booking_id
        )

        assert booking is not None
        assert booking.status == "CONFIRMED"


def test_cancel_booking(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    create_response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [seat_ids[0]]
        }
    )

    booking_id = (
        create_response
        .get_json()["data"]["id"]
    )

    response = authenticated_client.post(
        f"/api/v1/bookings/{booking_id}/cancel"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert (
        data["data"]["status"]
        == "CANCELLED"
    )


def test_cancelled_booking_cannot_be_cancelled_again(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    create_response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [seat_ids[0]]
        }
    )

    booking_id = (
        create_response
        .get_json()["data"]["id"]
    )

    first_cancel = authenticated_client.post(
        f"/api/v1/bookings/{booking_id}/cancel"
    )

    assert first_cancel.status_code == 200

    second_cancel = authenticated_client.post(
        f"/api/v1/bookings/{booking_id}/cancel"
    )

    assert second_cancel.status_code == 400

    data = second_cancel.get_json()

    assert data["status"] == "error"

    assert (
        data["message"]
        == "Only confirmed bookings can be cancelled"
    )


def test_booking_requires_authentication(
    client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    response = client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [seat_ids[0]]
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["status"] == "error"

    assert (
        data["message"]
        == "Authentication required"
    )


def test_get_bookings_requires_authentication(
    client
):

    response = client.get(
        "/api/v1/bookings"
    )

    assert response.status_code == 401


def test_missing_event_id(
    authenticated_client
):

    response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "seat_ids": [1]
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"

    assert (
        data["message"]
        == "event_id is required"
    )


def test_empty_seat_list(
    authenticated_client,
    app
):

    event_id, _ = get_event_and_seats(app)

    response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": []
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"

    assert (
        data["message"]
        == "At least one seat must be selected"
    )


def test_booking_unknown_event(
    authenticated_client
):

    response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": 999999,
            "seat_ids": [1]
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"

    assert (
        data["message"]
        == "Event not found"
    )

def test_seat_ids_must_be_a_list(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": seat_ids[0]
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "seat_ids must be a list"


def test_booking_unknown_seat(
    authenticated_client,
    app
):

    event_id, _ = get_event_and_seats(app)

    response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [999999]
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Seat 999999 not found"


def test_booking_inactive_seat(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    with app.app_context():

        seat = db.session.get(
            Seat,
            seat_ids[0]
        )

        seat.is_active = False

        db.session.commit()

    response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [seat_ids[0]]
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert (
        data["message"]
        == f"Seat {seat_ids[0]} is inactive"
    )


def test_booking_seat_from_another_venue(
    authenticated_client,
    app
):

    event_id, _ = get_event_and_seats(app)

    with app.app_context():

        other_venue = Venue(
            name="Other Venue",
            address="Other Address",
            city="Other City",
            capacity=10
        )

        db.session.add(other_venue)
        db.session.flush()

        other_seat = Seat(
            venue_id=other_venue.id,
            seat_number="OTHER-S1",
            row_number=1,
            seat_type="REGULAR",
            price=Decimal("500.00"),
            is_active=True
        )

        db.session.add(other_seat)
        db.session.commit()

        other_seat_id = other_seat.id

    response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [other_seat_id]
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert (
        data["message"]
        == f"Seat {other_seat_id} does not belong to the event venue"
    )


def test_already_booked_seat_cannot_be_booked_again(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    first_response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [seat_ids[0]]
        }
    )

    assert first_response.status_code == 201

    second_response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [seat_ids[0]]
        }
    )

    assert second_response.status_code == 400

    data = second_response.get_json()

    assert data["status"] == "error"
    assert (
        data["message"]
        == f"Seat {seat_ids[0]} is already booked"
    )


def test_duplicate_seat_ids_are_deduplicated(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [
                seat_ids[0],
                seat_ids[0],
                seat_ids[1]
            ]
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["status"] == "success"

    booking = data["data"]

    assert len(booking["seats"]) == 2

    assert (
        booking["total_amount"]
        == 3000.0
    )


def test_non_published_event_cannot_be_booked(
    authenticated_client,
    app
):

    event_id, seat_ids = get_event_and_seats(app)

    with app.app_context():

        event = db.session.get(
            Event,
            event_id
        )

        event.status = "DRAFT"

        db.session.commit()

    response = authenticated_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event_id,
            "seat_ids": [seat_ids[0]]
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert (
        data["message"]
        == "Event is not available for booking"
    )