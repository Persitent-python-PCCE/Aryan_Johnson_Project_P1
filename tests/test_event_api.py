# ============================================================
# EVENT API TESTS
# ============================================================


def test_get_events(customer_client):

    response = customer_client.get(
        "/api/v1/events"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert isinstance(
        data["data"],
        list
    )


def test_get_event_by_id(
    customer_client,
    event
):

    response = customer_client.get(
        f"/api/v1/events/{event.id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert (
        data["data"]["name"]
        == "Test Event"
    )


def test_get_unknown_event(
    customer_client
):

    response = customer_client.get(
        "/api/v1/events/99999"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"


def test_keyword_filter(
    customer_client
):

    response = customer_client.get(
        "/api/v1/events",
        query_string={
            "keyword": "Test"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(
        data["data"]
    ) >= 1


def test_date_filter(
    customer_client
):

    response = customer_client.get(
        "/api/v1/events",
        query_string={
            "event_date": "2026-12-15"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"


def test_invalid_date_filter(
    customer_client
):

    response = customer_client.get(
        "/api/v1/events",
        query_string={
            "event_date": "invalid-date"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_category_filter(
    customer_client,
    category
):

    response = customer_client.get(
        "/api/v1/events",
        query_string={
            "category_id": category.id
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"


def test_venue_filter(
    customer_client,
    venue
):

    response = customer_client.get(
        "/api/v1/events",
        query_string={
            "venue_id": venue.id
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"


def test_event_details_contains_name(
    customer_client,
    event
):

    response = customer_client.get(
        f"/api/v1/events/{event.id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert (
        data["data"]["name"]
        == "Test Event"
    )


def test_empty_search_returns_success(
    customer_client
):

    response = customer_client.get(
        "/api/v1/events",
        query_string={
            "keyword":
                "something-that-does-not-exist"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert data["data"] == []

def test_get_events_requires_authentication(
    client
):

    response = client.get(
        "/api/v1/events"
    )

    assert response.status_code == 401