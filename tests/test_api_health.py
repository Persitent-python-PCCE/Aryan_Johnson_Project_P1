import pytest

from app import create_app
from app.extensions import db


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
def client(app):
    return app.test_client()


def test_health_endpoint(client):

    response = client.get(
        "/api/v1/health"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert (
        data["message"]
        == "Ticket Booking API is running"
    )