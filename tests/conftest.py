import pytest

from datetime import date, time

from app import create_app
from app.extensions import db

from app.models.role import Role
from app.models.user import User
from app.models.category import Category
from app.models.venue import Venue
from app.models.event import Event
from app.models.seat import Seat

from werkzeug.security import generate_password_hash

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
)


@pytest.fixture
def app():
    app = create_app(
        test_config={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret",

            # JWT configuration
            "JWT_SECRET_KEY": "python -m pytest tests/test_admin_api.py -q",
            "JWT_TOKEN_LOCATION": ["cookies"],
            "JWT_COOKIE_SECURE": False,
            "JWT_COOKIE_CSRF_PROTECT": True,
            "JWT_COOKIE_SAMESITE": "Lax",
        }
    )

    with app.app_context():
        db.create_all()

        # ---------------------------------------------------------
        # Roles
        # ---------------------------------------------------------

        customer_role = Role(
            name="CUSTOMER",
            description="Customer"
        )

        admin_role = Role(
            name="ADMIN",
            description="Administrator"
        )

        db.session.add_all([
            customer_role,
            admin_role
        ])

        db.session.commit()

        # ---------------------------------------------------------
        # Users
        # ---------------------------------------------------------

        customer = User(
            name="Test Customer",
            email="customer@example.com",
            password_hash=generate_password_hash("password123"),
            role_id=customer_role.id,
            is_active=True
        )

        admin = User(
            name="Test Admin",
            email="admin@example.com",
            password_hash=generate_password_hash("password123"),
            role_id=admin_role.id,
            is_active=True
        )

        db.session.add_all([
            customer,
            admin
        ])

        db.session.commit()

        # ---------------------------------------------------------
        # Category
        # ---------------------------------------------------------

        category = Category(
            name="Test Category",
            description="Test category",
            is_active=True
        )

        db.session.add(category)
        db.session.commit()

        # ---------------------------------------------------------
        # Venue
        # ---------------------------------------------------------

        venue = Venue(
            name="Test Venue",
            address="123 Test Street",
            city="Bangalore",
            capacity=500,
            description="Test venue"
        )

        db.session.add(venue)
        db.session.commit()

        # ---------------------------------------------------------
        # Event
        # ---------------------------------------------------------

        event = Event(
            category_id=category.id,
            venue_id=venue.id,
            name="Test Event",
            description="Test event",
            event_date=date(2026, 12, 15),
            start_time=time(18, 0),
            end_time=time(20, 0),
            status="PUBLISHED"
        )

        db.session.add(event)
        db.session.commit()

        # ---------------------------------------------------------
        # Seats
        # ---------------------------------------------------------

        seats = [
            Seat(
                venue_id=venue.id,
                seat_number="A1",
                row_number=1,
                seat_type="REGULAR",
                price=500,
                is_active=True
            ),
            Seat(
                venue_id=venue.id,
                seat_number="A2",
                row_number=1,
                seat_type="REGULAR",
                price=500,
                is_active=True
            ),
            Seat(
                venue_id=venue.id,
                seat_number="A3",
                row_number=1,
                seat_type="VIP",
                price=1000,
                is_active=True
            ),
        ]


        db.session.add_all(seats)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ==============================================================
# JWT HELPERS
# ==============================================================

def _authenticate(client, app, user_id):

    with app.app_context():

        user = db.session.get(
            User,
            user_id
        )

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role.name,
                "email": user.email
            }
        )

        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role.name
            }
        )

        response = app.response_class()

        set_access_cookies(
            response,
            access_token
        )

        set_refresh_cookies(
            response,
            refresh_token
        )

        csrf_access_token = None
        csrf_refresh_token = None

        for header, value in response.headers:

            if header.lower() != "set-cookie":
                continue

            cookie_pair = value.split(
                ";",
                1
            )[0]

            name, cookie_value = cookie_pair.split(
                "=",
                1
            )

            client.set_cookie(
                name,
                cookie_value
            )

            if name == "csrf_access_token":
                csrf_access_token = cookie_value

            elif name == "csrf_refresh_token":
                csrf_refresh_token = cookie_value

        # Store the access CSRF token on the test client.
        client.environ_base[
            "HTTP_X_CSRF_TOKEN"
        ] = csrf_access_token

    return client


# ==============================================================
# USER FIXTURES
# ==============================================================

@pytest.fixture
def customer(app):
    with app.app_context():
        return User.query.filter_by(
            email="customer@example.com"
        ).first().id


@pytest.fixture
def admin(app):
    with app.app_context():
        return User.query.filter_by(
            email="admin@example.com"
        ).first().id


# ==============================================================
# AUTHENTICATED CLIENTS
# ==============================================================

@pytest.fixture
def customer_client(app, customer):
    client = app.test_client()
    return _authenticate(client, app, customer)


@pytest.fixture
def admin_client(app, admin):
    client = app.test_client()
    return _authenticate(client, app, admin)


# ==============================================================
# COMMON TEST DATA
# ==============================================================

@pytest.fixture
def category(app):
    with app.app_context():
        return Category.query.first()


@pytest.fixture
def venue(app):
    with app.app_context():
        return Venue.query.first()


@pytest.fixture
def event(app):
    with app.app_context():
        return Event.query.first()


@pytest.fixture
def seats(app):
    with app.app_context():
        return Seat.query.all()