def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
    )

    assert response.status_code in (200, 201)

    data = response.get_json()

    assert data["status"] == "success"


def test_register_duplicate_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Another User",
            "email": "customer@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_register_password_mismatch(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "New User",
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "different"
        }
    )

    assert response.status_code == 400


def test_register_missing_json(client):
    response = client.post(
        "/api/v1/auth/register"
    )

    assert response.status_code == 400


def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "customer@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"


def test_login_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "customer@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_login_unknown_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 400


def test_login_missing_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={}
    )

    assert response.status_code == 400


def test_login_sets_access_token_cookie(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "customer@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    cookies = response.headers.getlist("Set-Cookie")

    assert any(
        "access_token_cookie" in cookie
        for cookie in cookies
    )


def test_login_sets_refresh_token_cookie(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "customer@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    cookies = response.headers.getlist("Set-Cookie")

    assert any(
        "refresh_token_cookie" in cookie
        for cookie in cookies
    )


def test_refresh_requires_refresh_token(client):
    response = client.post(
        "/api/v1/auth/refresh"
    )

    assert response.status_code == 401


def test_logout_success(client):
    response = client.post(
        "/api/v1/auth/logout"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"