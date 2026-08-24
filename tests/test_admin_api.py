def test_admin_api_requires_authentication(client):

    response = client.get(
        "/api/v1/admin/categories"
    )

    assert response.status_code == 401


def test_customer_cannot_access_admin_api(customer_client):
    response = customer_client.get(
        "/api/v1/admin/categories"
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["status"] == "error"


def test_admin_can_get_categories(admin_client):
    response = admin_client.get(
        "/api/v1/admin/categories"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert isinstance(data["data"], list)


def test_admin_can_create_category(admin_client):
    response = admin_client.post(
        "/api/v1/admin/categories",
        json={
            "name": "Music",
            "description": "Music events"
        }
    )

    assert response.status_code in (200, 201)

    data = response.get_json()

    assert data["status"] == "success"


def test_admin_create_category_requires_name(admin_client):
    response = admin_client.post(
        "/api/v1/admin/categories",
        json={
            "description": "Missing name"
        }
    )

    assert response.status_code == 400


def test_admin_cannot_create_duplicate_category(admin_client):
    response = admin_client.post(
        "/api/v1/admin/categories",
        json={
            "name": "Test Category",
            "description": "Duplicate"
        }
    )

    assert response.status_code == 400


def test_admin_can_get_category(admin_client, category):
    response = admin_client.get(
        f"/api/v1/admin/categories/{category.id}"
    )

    assert response.status_code == 200


def test_admin_get_unknown_category(admin_client):
    response = admin_client.get(
        "/api/v1/admin/categories/99999"
    )

    assert response.status_code == 404


def test_admin_can_update_category(admin_client, category):
    response = admin_client.put(
        f"/api/v1/admin/categories/{category.id}",
        json={
            "description": "Updated description"
        }
    )

    assert response.status_code == 200


def test_admin_can_delete_category(admin_client):
    response = admin_client.post(
        "/api/v1/admin/categories",
        json={
            "name": "Delete Me"
        }
    )

    assert response.status_code in (200, 201)

    category_id = response.get_json()["data"]["id"]

    response = admin_client.delete(
        f"/api/v1/admin/categories/{category_id}"
    )

    assert response.status_code == 200


# ============================================================
# VENUES
# ============================================================

def test_admin_can_get_venues(admin_client):
    response = admin_client.get(
        "/api/v1/admin/venues"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"


def test_admin_can_create_venue(admin_client):
    response = admin_client.post(
        "/api/v1/admin/venues",
        json={
            "name": "New Venue",
            "address": "123 Main Street",
            "city": "Bangalore",
            "capacity": 100
        }
    )

    assert response.status_code in (200, 201)


def test_admin_create_venue_requires_capacity(admin_client):
    response = admin_client.post(
        "/api/v1/admin/venues",
        json={
            "name": "Invalid Venue",
            "address": "Address",
            "city": "Bangalore"
        }
    )

    assert response.status_code == 400


def test_admin_create_venue_rejects_invalid_capacity(admin_client):
    response = admin_client.post(
        "/api/v1/admin/venues",
        json={
            "name": "Invalid Venue",
            "address": "Address",
            "city": "Bangalore",
            "capacity": -10
        }
    )

    assert response.status_code == 400


def test_admin_can_get_venue(admin_client, venue):
    response = admin_client.get(
        f"/api/v1/admin/venues/{venue.id}"
    )

    assert response.status_code == 200


def test_admin_get_unknown_venue(admin_client):
    response = admin_client.get(
        "/api/v1/admin/venues/99999"
    )

    assert response.status_code == 404


# ============================================================
# EVENTS
# ============================================================

def test_admin_can_get_events(admin_client):
    response = admin_client.get(
        "/api/v1/admin/events"
    )

    assert response.status_code == 200


def test_admin_can_create_event(admin_client, category, venue):
    response = admin_client.post(
        "/api/v1/admin/events",
        json={
            "category_id": category.id,
            "venue_id": venue.id,
            "name": "Admin Test Event",
            "description": "Created through API",
            "event_date": "2027-01-15",
            "start_time": "18:00",
            "end_time": "20:00",
            "status": "DRAFT"
        }
    )

    assert response.status_code in (200, 201)


def test_admin_create_event_requires_required_fields(admin_client):
    response = admin_client.post(
        "/api/v1/admin/events",
        json={
            "name": "Incomplete Event"
        }
    )

    assert response.status_code == 400


def test_admin_can_get_event(admin_client, event):
    response = admin_client.get(
        f"/api/v1/admin/events/{event.id}"
    )

    assert response.status_code == 200