import pytest

from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.user import User
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

        role = Role(
            name="CUSTOMER",
            description="Customer"
        )

        db.session.add(role)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_page_loads(client):
    response = client.get(
        "/auth/register"
    )

    assert response.status_code == 200
    assert b"Create Account" in response.data


def test_register_creates_customer(
    client,
    app
):
    response = client.post(
        "/auth/register",
        data={
            "name": "Test Customer",
            "email": "customer@example.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert (
        b"Registration successful"
        in response.data
    )

    with app.app_context():
        user = User.query.filter_by(
            email="customer@example.com"
        ).first()

        assert user is not None
        assert user.name == "Test Customer"

        assert user.password_hash != "password123"

        assert user.role.name == "CUSTOMER"


def test_register_rejects_password_mismatch(
    client
):
    response = client.post(
        "/auth/register",
        data={
            "name": "Test Customer",
            "email": "mismatch@example.com",
            "password": "password123",
            "confirm_password": "different123"
        }
    )

    assert response.status_code == 200
    assert (
        b"Passwords do not match"
        in response.data
    )


def test_register_rejects_duplicate_email(
    client
):
    client.post(
        "/auth/register",
        data={
            "name": "First User",
            "email": "duplicate@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
    )

    response = client.post(
        "/auth/register",
        data={
            "name": "Second User",
            "email": "duplicate@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
    )

    assert response.status_code == 200
    assert (
        b"Email already exists"
        in response.data
    )


def test_login_page_loads(client):
    response = client.get(
        "/auth/login"
    )

    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_creates_session(
    client,
    app
):
    with app.app_context():
        AuthService.register(
            name="Login Customer",
            email="login@example.com",
            password="password123"
        )

        db.session.commit()

    response = client.post(
        "/auth/login",
        data={
            "email": "login@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session["user_id"] is not None
        assert session["role"] == "CUSTOMER"


def test_login_rejects_invalid_password(
    client,
    app
):
    with app.app_context():
        AuthService.register(
            name="Invalid Login",
            email="invalid@example.com",
            password="password123"
        )

        db.session.commit()

    response = client.post(
        "/auth/login",
        data={
            "email": "invalid@example.com",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 200
    assert (
        b"Invalid email or password"
        in response.data
    )

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/auth/login",
        data={
            "email": "unknown@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert (
        b"Invalid email or password"
        in response.data
    )

    with client.session_transaction() as session:
        assert "user_id" not in session