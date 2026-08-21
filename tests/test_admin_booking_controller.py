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

from app.services.booking_service import BookingService


# ============================================================================
# Fixtures
# ============================================================================

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

        db.session.add(customer_role)
        db.session.add(admin_role)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ============================================================================
# Test data helpers
# ============================================================================

def create_customer():
    role = Role.query.filter_by(
        name="CUSTOMER"
    ).first()

    customer = User(
        name="Test Customer",
        email="admin-booking-customer@example.com",
        password_hash="test-password-hash",
        role_id=role.id,
        is_active=True
    )

    db.session.add(customer)
    db.session.commit()

    return customer


def create_admin():
    role = Role.query.filter_by(
        name="ADMIN"
    ).first()

    admin = User(
        name="Test Admin",
        email="admin-booking-admin@example.com",
        password_hash="test-password-hash",
        role_id=role.id,
        is_active=True
    )

    db.session.add(admin)
    db.session.commit()

    return admin


def login_as(client, user):
    with client.session_transaction() as session:
        session.clear()

        session["user_id"] = user.id
        session["role"] = user.role.name


def create_booking(customer):
    category = Category(
        name="Test Booking Category",
        description="Category for admin booking tests",
        is_active=True
    )

    venue = Venue(
        name="Test Booking Venue",
        address="Test Address",
        city="Test City",
        capacity=10,
        description="Venue for admin booking tests"
    )

    db.session.add(category)
    db.session.add(venue)
    db.session.flush()

    event = Event(
        category_id=category.id,
        venue_id=venue.id,
        name="Test Booking Event",
        description="Event for admin booking tests",
        event_date=date(2026, 12, 1),
        start_time=time(18, 0),
        end_time=time(20, 0),
        status="PUBLISHED"
    )

    db.session.add(event)
    db.session.flush()

    seat = Seat(
        venue_id=venue.id,
        seat_number="TEST-S1",
        row_number=1,
        seat_type="REGULAR",
        price=Decimal("500.00"),
        is_active=True
    )

    db.session.add(seat)
    db.session.commit()

    booking = BookingService.create_booking(
        user_id=customer.id,
        event_id=event.id,
        seat_ids=[seat.id]
    )

    return booking


# ============================================================================
# Admin booking list
# ============================================================================

def test_admin_can_view_bookings(
    client,
    app
):
    with app.app_context():

        customer = create_customer()
        admin = create_admin()

        booking = create_booking(
            customer
        )

        login_as(
            client,
            admin
        )

        response = client.get(
            "/admin/bookings"
        )

        assert response.status_code == 200

        assert (
            booking.booking_reference.encode()
            in response.data
        )

        assert (
            b"Test Booking Event"
            in response.data
        )


# ============================================================================
# Status filtering
# ============================================================================

def test_admin_can_filter_confirmed_bookings(
    client,
    app
):
    with app.app_context():

        customer = create_customer()
        admin = create_admin()

        booking = create_booking(
            customer
        )

        login_as(
            client,
            admin
        )

        response = client.get(
            "/admin/bookings",
            query_string={
                "status": "CONFIRMED"
            }
        )

        assert response.status_code == 200

        assert (
            booking.booking_reference.encode()
            in response.data
        )


def test_admin_can_filter_cancelled_bookings(
    client,
    app
):
    with app.app_context():

        customer = create_customer()
        admin = create_admin()

        booking = create_booking(
            customer
        )

        BookingService.cancel_booking(
            booking.id
        )

        login_as(
            client,
            admin
        )

        response = client.get(
            "/admin/bookings",
            query_string={
                "status": "CANCELLED"
            }
        )

        assert response.status_code == 200

        assert (
            booking.booking_reference.encode()
            in response.data
        )


# ============================================================================
# Booking reference search
# ============================================================================

def test_admin_can_search_booking_by_reference(
    client,
    app
):
    with app.app_context():

        customer = create_customer()
        admin = create_admin()

        booking = create_booking(
            customer
        )

        reference_fragment = (
            booking.booking_reference[3:10]
        )

        login_as(
            client,
            admin
        )

        response = client.get(
            "/admin/bookings",
            query_string={
                "booking_reference": reference_fragment
            }
        )

        assert response.status_code == 200

        assert (
            booking.booking_reference.encode()
            in response.data
        )


def test_admin_search_returns_no_results_for_unknown_reference(
    client,
    app
):
    with app.app_context():

        admin = create_admin()

        login_as(
            client,
            admin
        )

        response = client.get(
            "/admin/bookings",
            query_string={
                "booking_reference": "BK-DOES-NOT-EXIST"
            }
        )

        assert response.status_code == 200

        assert (
            b"No bookings found."
            in response.data
        )


# ============================================================================
# Booking details
# ============================================================================

def test_admin_can_view_booking_details(
    client,
    app
):
    with app.app_context():

        customer = create_customer()
        admin = create_admin()

        booking = create_booking(
            customer
        )

        login_as(
            client,
            admin
        )

        response = client.get(
            f"/admin/bookings/{booking.id}"
        )

        assert response.status_code == 200

        assert (
            booking.booking_reference.encode()
            in response.data
        )

        assert (
            b"Test Customer"
            in response.data
        )

        assert (
            b"admin-booking-customer@example.com"
            in response.data
        )

        assert (
            b"Test Booking Event"
            in response.data
        )

        assert (
            b"TEST-S1"
            in response.data
        )


def test_admin_booking_details_returns_redirect_for_unknown_booking(
    client,
    app
):
    with app.app_context():

        admin = create_admin()

        login_as(
            client,
            admin
        )

        response = client.get(
            "/admin/bookings/999999"
        )

        assert response.status_code == 302

        assert (
            "/admin/bookings"
            in response.location
        )


# ============================================================================
# Admin cancellation
# ============================================================================

def test_admin_can_cancel_confirmed_booking(
    client,
    app
):
    with app.app_context():

        customer = create_customer()
        admin = create_admin()

        booking = create_booking(
            customer
        )

        assert booking.status == "CONFIRMED"

        login_as(
            client,
            admin
        )

        response = client.post(
            f"/admin/bookings/{booking.id}/cancel"
        )

        assert response.status_code == 302

        db.session.refresh(
            booking
        )

        assert booking.status == "CANCELLED"

        assert (
            booking.cancelled_at is not None
        )


def test_admin_cannot_cancel_already_cancelled_booking(
    client,
    app
):
    with app.app_context():

        customer = create_customer()
        admin = create_admin()

        booking = create_booking(
            customer
        )

        BookingService.cancel_booking(
            booking.id
        )

        db.session.refresh(
            booking
        )

        cancelled_at = booking.cancelled_at

        login_as(
            client,
            admin
        )

        response = client.post(
            f"/admin/bookings/{booking.id}/cancel"
        )

        assert response.status_code == 302

        db.session.refresh(
            booking
        )

        assert booking.status == "CANCELLED"

        assert (
            booking.cancelled_at == cancelled_at
        )


def test_admin_cancel_unknown_booking(
    client,
    app
):
    with app.app_context():

        admin = create_admin()

        login_as(
            client,
            admin
        )

        response = client.post(
            "/admin/bookings/999999/cancel"
        )

        assert response.status_code == 302

        assert (
            "/admin/bookings"
            in response.location
        )


# ============================================================================
# Authorization
# ============================================================================

def test_customer_cannot_access_admin_bookings(
    client,
    app
):
    with app.app_context():

        customer = create_customer()

        login_as(
            client,
            customer
        )

        response = client.get(
            "/admin/bookings"
        )

        assert response.status_code == 302


def test_customer_cannot_view_admin_booking_details(
    client,
    app
):
    with app.app_context():

        customer = create_customer()

        booking = create_booking(
            customer
        )

        login_as(
            client,
            customer
        )

        response = client.get(
            f"/admin/bookings/{booking.id}"
        )

        assert response.status_code == 302


def test_customer_cannot_cancel_booking_from_admin_route(
    client,
    app
):
    with app.app_context():

        customer = create_customer()

        booking = create_booking(
            customer
        )

        login_as(
            client,
            customer
        )

        response = client.post(
            f"/admin/bookings/{booking.id}/cancel"
        )

        assert response.status_code == 302

        db.session.refresh(
            booking
        )

        assert booking.status == "CONFIRMED"


def test_unauthenticated_user_cannot_access_admin_bookings(
    client,
    app
):
    with app.app_context():

        with client.session_transaction() as session:
            session.clear()

        response = client.get(
            "/admin/bookings"
        )

        assert response.status_code in (
            302,
            401,
            403
        )