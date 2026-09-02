from flask import jsonify, request

from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    verify_jwt_in_request
)

from app.controllers.api import api_bp
from app.services.booking_service import BookingService


def get_authenticated_customer_id():

    verify_jwt_in_request()

    identity = get_jwt_identity()
    claims = get_jwt()

    # Only CUSTOMER users may access booking APIs.
    if claims.get("role") != "CUSTOMER":
        return None

    try:
        return int(identity)

    except (TypeError, ValueError):
        return None


def serialize_booking(booking):
    """
    Convert a Booking model into a JSON-serializable dictionary.
    """

    return {
        "id": booking.id,

        "booking_reference": (
            booking.booking_reference
        ),

        "event": {
            "id": booking.event.id,

            "name": booking.event.name,

            "event_date": (
                booking.event.event_date.isoformat()
                if booking.event.event_date
                else None
            ),

            "start_time": (
                booking.event.start_time.isoformat()
                if booking.event.start_time
                else None
            ),

            "end_time": (
                booking.event.end_time.isoformat()
                if booking.event.end_time
                else None
            )
        },

        "total_amount": float(
            booking.total_amount
        ),

        "status": booking.status,

        "booked_at": (
            booking.booked_at.isoformat()
            if booking.booked_at
            else None
        ),

        "cancelled_at": (
            booking.cancelled_at.isoformat()
            if booking.cancelled_at
            else None
        ),

        "seats": [
            {
                "id": item.seat.id,

                "seat_number": (
                    item.seat.seat_number
                ),

                "row_number": (
                    item.seat.row_number
                ),

                "seat_type": (
                    item.seat.seat_type
                ),

                "price": float(
                    item.price
                )
            }

            for item in booking.items
        ]
    }


@api_bp.route(
    "/bookings",
    methods=["POST"]
)
def create_booking():
    """
    Create a booking for the authenticated customer.
    """

    user_id = get_authenticated_customer_id()

    if user_id is None:
        return jsonify({
            "status": "error",
            "message": "Customer access required"
        }), 403

    data = request.get_json(
        silent=True
    )

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON"
        }), 400

    event_id = data.get(
        "event_id"
    )

    seat_ids = data.get(
        "seat_ids"
    )

    if event_id is None:
        return jsonify({
            "status": "error",
            "message": "event_id is required"
        }), 400

    if not isinstance(
        seat_ids,
        list
    ):
        return jsonify({
            "status": "error",
            "message": "seat_ids must be a list"
        }), 400

    try:

        event_id = int(
            event_id
        )

        seat_ids = [
            int(seat_id)
            for seat_id in seat_ids
        ]

        booking = (
            BookingService.create_booking(
                user_id=user_id,
                event_id=event_id,
                seat_ids=seat_ids
            )
        )

        return jsonify({
            "status": "success",
            "message": "Booking created successfully",
            "data": serialize_booking(
                booking
            )
        }), 201

    except (
        ValueError,
        TypeError
    ) as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


@api_bp.route(
    "/bookings",
    methods=["GET"]
)
def get_bookings():
    """
    Return bookings belonging only to the authenticated customer.
    """

    user_id = get_authenticated_customer_id()

    if user_id is None:
        return jsonify({
            "status": "error",
            "message": "Customer access required"
        }), 403

    bookings = (
        BookingService.get_user_bookings(
            user_id
        )
    )

    return jsonify({
        "status": "success",
        "data": [
            serialize_booking(
                booking
            )

            for booking in bookings
        ]
    }), 200


@api_bp.route(
    "/bookings/<int:booking_id>",
    methods=["GET"]
)
def get_booking(booking_id):
    """
    Return a booking only when it belongs to
    the authenticated customer.
    """

    user_id = get_authenticated_customer_id()

    if user_id is None:
        return jsonify({
            "status": "error",
            "message": "Customer access required"
        }), 403

    try:

        booking = (
            BookingService.get_booking(
                booking_id
            )
        )

        # Prevent customers from accessing
        # another customer's booking.
        if booking.user_id != user_id:

            return jsonify({
                "status": "error",
                "message": "Booking not found"
            }), 404

        return jsonify({
            "status": "success",
            "data": serialize_booking(
                booking
            )
        }), 200

    except ValueError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 404


@api_bp.route(
    "/bookings/<int:booking_id>/cancel",
    methods=["POST"]
)
def cancel_booking(booking_id):
    """
    Cancel a booking belonging to the authenticated customer.
    """

    user_id = get_authenticated_customer_id()

    if user_id is None:
        return jsonify({
            "status": "error",
            "message": "Customer access required"
        }), 403

    try:

        booking = (
            BookingService.get_booking(
                booking_id
            )
        )

        # Prevent customers from cancelling
        # another customer's booking.
        if booking.user_id != user_id:

            return jsonify({
                "status": "error",
                "message": "Booking not found"
            }), 404

        booking = (
            BookingService.cancel_booking(
                booking_id
            )
        )

        return jsonify({
            "status": "success",
            "message": "Booking cancelled successfully",
            "data": serialize_booking(
                booking
            )
        }), 200

    except ValueError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400