from datetime import date, time

import pytest

from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.category import Category
from app.models.venue import Venue
from app.models.event import Event


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
            name="Test Category",
            description="Test category",
            is_active=True
        )

        venue = Venue(
            name="Test Venue",
            address="Test Address",
            city="Test City",
            capacity=100
        )

        db.session.add(role)
        db.session.add(category)
        db.session.add(venue)
        db.session.flush()

        published_event = Event(
            category_id=category.id,
            venue_id=venue.id,
            name="Published Test Event",
            description="Published event",
            event_date=date(2026, 12, 1),
            start_time=time(18, 0),
            end_time=time(20, 0),
            status="PUBLISHED"
        )

        draft_event = Event(
            category_id=category.id,
            venue_id=venue.id,
            name="Draft Test Event",
            description="Draft event",
            event_date=date(2026, 12, 2),
            start_time=time(18, 0),
            end_time=time(20, 0),
            status="DRAFT"
        )

        db.session.add(published_event)
        db.session.add(draft_event)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_events(client):

    response = client.get(
        "/api/v1/events"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert len(data["data"]) == 1

    assert (
        data["data"][0]["name"]
        == "Published Test Event"
    )


def test_get_event_by_id(
    client,
    app
):

    with app.app_context():

        event = Event.query.filter_by(
            name="Published Test Event"
        ).first()

        event_id = event.id

    response = client.get(
        f"/api/v1/events/{event_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert (
        data["data"]["name"]
        == "Published Test Event"
    )


def test_get_unknown_event(client):

    response = client.get(
        "/api/v1/events/999999"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"

    assert data["message"] == "Event not found"


def test_draft_event_is_not_exposed(
    client,
    app
):

    with app.app_context():

        draft_event = Event.query.filter_by(
            name="Draft Test Event"
        ).first()

        event_id = draft_event.id

    response = client.get(
        f"/api/v1/events/{event_id}"
    )

    assert response.status_code == 404


def test_keyword_filter(client):

    response = client.get(
        "/api/v1/events",
        query_string={
            "keyword": "Published"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["data"]) == 1

    assert (
        data["data"][0]["name"]
        == "Published Test Event"
    )


def test_date_filter(client):

    response = client.get(
        "/api/v1/events",
        query_string={
            "event_date": "2026-12-01"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["data"]) == 1


def test_invalid_date_returns_400(client):

    response = client.get(
        "/api/v1/events",
        query_string={
            "event_date": "invalid-date"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_invalid_page_returns_400(client):

    response = client.get(
        "/api/v1/events",
        query_string={
            "page": 0
        }
    )

    assert response.status_code == 400


def test_invalid_per_page_returns_400(client):

    response = client.get(
        "/api/v1/events",
        query_string={
            "per_page": 101
        }
    )

    assert response.status_code == 400


def test_pagination_metadata(client):

    response = client.get(
        "/api/v1/events",
        query_string={
            "page": 1,
            "per_page": 10
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "pagination" in data

    assert (
        data["pagination"]["page"]
        == 1
    )

    assert (
        data["pagination"]["per_page"]
        == 10
    )

    assert (
        data["pagination"]["total"]
        == 1
    )