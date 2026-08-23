import pytest

from app import create_app
from app.extensions import db

from app.models.role import Role
from app.models.user import User
from app.models.category import Category
from app.models.venue import Venue
from app.models.event import Event

from werkzeug.security import generate_password_hash

from datetime import date, time


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

        admin_role = Role(
            name="ADMIN",
            description="Administrator"
        )

        customer_role = Role(
            name="CUSTOMER",
            description="Customer"
        )

        db.session.add_all([
            admin_role,
            customer_role
        ])

        db.session.commit()

        admin = User(
            name="Test Admin",
            email="admin@example.com",
            password_hash=generate_password_hash(
                "password123"
            ),
            role_id=admin_role.id
        )

        customer = User(
            name="Test Customer",
            email="customer@example.com",
            password_hash=generate_password_hash(
                "password123"
            ),
            role_id=customer_role.id
        )

        category = Category(
            name="Test Category",
            description="Test category"
        )

        venue = Venue(
            name="Test Venue",
            address="123 Test Street",
            city="Bangalore",
            capacity=500,
            description="Test venue"
        )

        db.session.add_all([
            admin,
            customer,
            category,
            venue
        ])

        db.session.commit()

        event = Event(
            category_id=category.id,
            venue_id=venue.id,
            name="Test Event",
            description="Test event",
            event_date=date(2026, 12, 15),
            start_time=time(18, 0),
            end_time=time(20, 0),
            status="DRAFT"
        )

        db.session.add(event)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_client(app):
    client = app.test_client()

    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "ADMIN"

    return client


@pytest.fixture
def customer_client(app):
    client = app.test_client()

    with client.session_transaction() as session:
        session["user_id"] = 2
        session["role"] = "CUSTOMER"

    return client


# ============================================================
# AUTHORIZATION
# ============================================================


def test_admin_api_requires_authentication(client):

    response = client.get(
        "/api/v1/admin/categories"
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Authentication required"


def test_customer_cannot_access_admin_api(
    customer_client
):

    response = customer_client.get(
        "/api/v1/admin/categories"
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Admin access required"


# ============================================================
# CATEGORY API
# ============================================================


def test_admin_can_get_categories(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/categories"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1

    assert data["data"][0]["name"] == "Test Category"


def test_admin_can_create_category(
    admin_client,
    app
):

    response = admin_client.post(
        "/api/v1/admin/categories",
        json={
            "name": "Sports",
            "description": "Sports events"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["status"] == "success"
    assert data["message"] == (
        "Category created successfully"
    )

    assert data["data"]["name"] == "Sports"
    assert data["data"]["description"] == "Sports events"

    with app.app_context():

        category = Category.query.filter_by(
            name="Sports"
        ).first()

        assert category is not None


def test_admin_create_category_requires_name(
    admin_client
):

    response = admin_client.post(
        "/api/v1/admin/categories",
        json={
            "description": "Missing name"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Name is required"


def test_admin_cannot_create_duplicate_category(
    admin_client
):

    response = admin_client.post(
        "/api/v1/admin/categories",
        json={
            "name": "Test Category"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Category already exists"


def test_admin_can_get_category(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/categories/1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == 1
    assert data["data"]["name"] == "Test Category"


def test_admin_get_unknown_category_returns_404(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/categories/9999"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Category not found"


def test_admin_can_update_category(
    admin_client,
    app
):

    response = admin_client.put(
        "/api/v1/admin/categories/1",
        json={
            "name": "Updated Category",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["message"] == (
        "Category updated successfully"
    )

    assert data["data"]["name"] == "Updated Category"

    with app.app_context():

        category = db.session.get(
            Category,
            1
        )

        assert category.name == "Updated Category"


def test_admin_can_delete_category(
    admin_client,
    app
):
    with app.app_context():
        event = db.session.get(
            Event,
            1
        )

        if event:
            db.session.delete(event)
            db.session.commit()

    response = admin_client.delete(
        "/api/v1/admin/categories/1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["message"] == (
        "Category deleted successfully"
    )

    with app.app_context():
        category = db.session.get(
            Category,
            1
        )

        assert category is None


# ============================================================
# VENUE API
# ============================================================


def test_admin_can_get_venues(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/venues"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1

    assert data["data"][0]["name"] == "Test Venue"


def test_admin_can_create_venue(
    admin_client,
    app
):

    response = admin_client.post(
        "/api/v1/admin/venues",
        json={
            "name": "API Venue",
            "address": "456 API Street",
            "city": "Mangalore",
            "capacity": 1000,
            "description": "API test venue"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["status"] == "success"
    assert data["message"] == (
        "Venue created successfully"
    )

    assert data["data"]["name"] == "API Venue"
    assert data["data"]["capacity"] == 1000

    with app.app_context():

        venue = Venue.query.filter_by(
            name="API Venue"
        ).first()

        assert venue is not None


def test_admin_create_venue_requires_capacity(
    admin_client
):

    response = admin_client.post(
        "/api/v1/admin/venues",
        json={
            "name": "Invalid Venue",
            "address": "Address",
            "city": "City"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Capacity is required"


def test_admin_create_venue_rejects_invalid_capacity(
    admin_client
):

    response = admin_client.post(
        "/api/v1/admin/venues",
        json={
            "name": "Invalid Venue",
            "address": "Address",
            "city": "City",
            "capacity": 0
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_admin_can_get_venue(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/venues/1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == 1
    assert data["data"]["name"] == "Test Venue"


def test_admin_get_unknown_venue_returns_404(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/venues/9999"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Venue not found"


def test_admin_can_update_venue(
    admin_client,
    app
):

    response = admin_client.put(
        "/api/v1/admin/venues/1",
        json={
            "name": "Updated Venue",
            "address": "789 Updated Street",
            "city": "Goa",
            "capacity": 750,
            "description": "Updated venue"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["message"] == (
        "Venue updated successfully"
    )

    assert data["data"]["name"] == "Updated Venue"
    assert data["data"]["capacity"] == 750

    with app.app_context():

        venue = db.session.get(
            Venue,
            1
        )

        assert venue.name == "Updated Venue"
        assert venue.capacity == 750


def test_admin_can_delete_venue(
    admin_client,
    app
):

    # Delete the event first because it references
    # this venue through a foreign key.

    event = None

    with app.app_context():

        event = db.session.get(
            Event,
            1
        )

        if event:
            db.session.delete(event)
            db.session.commit()

    response = admin_client.delete(
        "/api/v1/admin/venues/1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["message"] == (
        "Venue deleted successfully"
    )

    with app.app_context():

        venue = db.session.get(
            Venue,
            1
        )

        assert venue is None


# ============================================================
# EVENT API
# ============================================================


def test_admin_can_get_events(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/events"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert isinstance(data["data"], list)

    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 10
    assert data["pagination"]["total"] == 1


def test_admin_can_filter_events_by_status(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/events?status=DRAFT"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert len(data["data"]) == 1
    assert data["data"][0]["status"] == "DRAFT"


def test_admin_can_filter_events_by_category(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/events?category_id=1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert len(data["data"]) == 1

    assert data["data"][0]["category"]["id"] == 1


def test_admin_can_filter_events_by_venue(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/events?venue_id=1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert len(data["data"]) == 1

    assert data["data"][0]["venue"]["id"] == 1


def test_admin_can_search_events_by_keyword(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/events?keyword=Test"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert len(data["data"]) == 1

    assert data["data"][0]["name"] == "Test Event"


def test_admin_can_filter_events_by_date(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/events?event_date=2026-12-15"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert len(data["data"]) == 1


def test_admin_rejects_invalid_event_date(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/events?event_date=invalid-date"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == (
        "Invalid event_date format. Use YYYY-MM-DD"
    )


def test_admin_can_create_event(
    admin_client,
    app
):

    response = admin_client.post(
        "/api/v1/admin/events",
        json={
            "category_id": 1,
            "venue_id": 1,
            "name": "New API Event",
            "description": "Created through API",
            "event_date": "2026-12-20",
            "start_time": "19:00:00",
            "end_time": "21:00:00",
            "status": "DRAFT"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["status"] == "success"
    assert data["message"] == (
        "Event created successfully"
    )

    assert data["data"]["name"] == "New API Event"
    assert data["data"]["status"] == "DRAFT"

    with app.app_context():

        event = Event.query.filter_by(
            name="New API Event"
        ).first()

        assert event is not None


def test_admin_create_event_requires_fields(
    admin_client
):

    response = admin_client.post(
        "/api/v1/admin/events",
        json={
            "name": "Incomplete Event"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_admin_create_event_rejects_invalid_status(
    admin_client
):

    response = admin_client.post(
        "/api/v1/admin/events",
        json={
            "category_id": 1,
            "venue_id": 1,
            "name": "Invalid Status Event",
            "event_date": "2026-12-20",
            "start_time": "19:00:00",
            "end_time": "21:00:00",
            "status": "INVALID"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Invalid event status"


def test_admin_can_get_event(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/events/1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == 1
    assert data["data"]["name"] == "Test Event"


def test_admin_get_unknown_event_returns_404(
    admin_client
):

    response = admin_client.get(
        "/api/v1/admin/events/9999"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Event not found"


def test_admin_can_update_event(
    admin_client,
    app
):

    response = admin_client.put(
        "/api/v1/admin/events/1",
        json={
            "category_id": 1,
            "venue_id": 1,
            "name": "Updated API Event",
            "description": "Updated through API",
            "event_date": "2026-12-25",
            "start_time": "20:00:00",
            "end_time": "22:00:00",
            "status": "PUBLISHED"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["message"] == (
        "Event updated successfully"
    )

    assert data["data"]["name"] == "Updated API Event"
    assert data["data"]["status"] == "PUBLISHED"

    with app.app_context():

        event = db.session.get(
            Event,
            1
        )

        assert event.name == "Updated API Event"
        assert event.status == "PUBLISHED"


def test_admin_update_event_requires_fields(
    admin_client
):

    response = admin_client.put(
        "/api/v1/admin/events/1",
        json={
            "name": "Incomplete Update"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_admin_update_event_rejects_invalid_status(
    admin_client
):

    response = admin_client.put(
        "/api/v1/admin/events/1",
        json={
            "category_id": 1,
            "venue_id": 1,
            "name": "Invalid Update",
            "event_date": "2026-12-25",
            "start_time": "20:00:00",
            "end_time": "22:00:00",
            "status": "INVALID"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Invalid event status"


def test_admin_can_delete_draft_event(
    admin_client,
    app
):

    response = admin_client.delete(
        "/api/v1/admin/events/1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["message"] == (
        "Event deleted successfully"
    )

    with app.app_context():

        event = db.session.get(
            Event,
            1
        )

        assert event is None


def test_admin_cannot_delete_published_event(
    admin_client,
    app
):

    with app.app_context():
        event = db.session.get(
            Event,
            1
        )

        event.status = "PUBLISHED"

        db.session.commit()

    response = admin_client.delete(
        "/api/v1/admin/events/1"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == (
        "Published events cannot be deleted"
    )