def test_booking_requires_authentication(client, event, seats):
    response = client.post(
        "/api/v1/bookings",
        json={
            "event_id": event.id,
            "seat_ids": [seats[0].id]
        }
    )

    assert response.status_code == 401


def test_customer_can_create_booking(
    customer_client,
    event,
    seats
):
    response = customer_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event.id,
            "seat_ids": [seats[0].id]
        }
    )

    assert response.status_code in (200, 201)

    data = response.get_json()

    assert data["status"] == "success"


def test_booking_requires_event_id(customer_client, seats):
    response = customer_client.post(
        "/api/v1/bookings",
        json={
            "seat_ids": [seats[0].id]
        }
    )

    assert response.status_code == 400


def test_booking_requires_seat_ids(customer_client, event):
    response = customer_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event.id
        }
    )

    assert response.status_code == 400


def test_booking_rejects_empty_seat_list(
    customer_client,
    event
):
    response = customer_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event.id,
            "seat_ids": []
        }
    )

    assert response.status_code == 400


def test_customer_can_view_booking_history(
    customer_client
):
    response = customer_client.get(
        "/api/v1/bookings"
    )

    assert response.status_code == 200


def test_customer_can_cancel_booking(
    customer_client,
    event,
    seats
):
    # --------------------------------------------------------
    # 1. Create booking
    # --------------------------------------------------------

    response = customer_client.post(
        "/api/v1/bookings",
        json={
            "event_id": event.id,
            "seat_ids": [seats[0].id]
        }
    )

    assert response.status_code in (200, 201)

    data = response.get_json()

    booking_id = data["data"]["id"]

    assert data["data"]["status"] == "PENDING_PAYMENT"

    # --------------------------------------------------------
    # 2. Initiate mock payment
    # --------------------------------------------------------

    response = customer_client.post(
        f"/api/v1/bookings/{booking_id}/payment",
        json={
            "payment_method": "UPI"
        }
    )

    assert response.status_code in (200, 201), (
        f"Payment initiation failed: "
        f"{response.status_code} "
        f"{response.get_json()}"
    )

    # --------------------------------------------------------
    # 3. Process successful mock payment
    # --------------------------------------------------------

    response = customer_client.post(
        f"/api/v1/bookings/{booking_id}/payment/process",
        json={
            "success": True
        }
    )

    assert response.status_code == 200, (
        f"Payment processing failed: "
        f"{response.status_code} "
        f"{response.get_json()}"
    )

    data = response.get_json()

    assert data["status"] == "success"

    # --------------------------------------------------------
    # 4. Verify booking is confirmed
    # --------------------------------------------------------

    response = customer_client.get(
        f"/api/v1/bookings/{booking_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["data"]["status"] == "CONFIRMED"

    # --------------------------------------------------------
    # 5. Cancel confirmed booking
    # --------------------------------------------------------

    response = customer_client.post(
        f"/api/v1/bookings/{booking_id}/cancel"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["status"] == "CANCELLED"


def test_get_unknown_booking(customer_client):
    response = customer_client.get(
        "/api/v1/bookings/99999"
    )

    assert response.status_code == 404