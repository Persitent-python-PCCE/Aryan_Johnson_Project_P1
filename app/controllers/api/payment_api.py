from flask import jsonify, request

from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    verify_jwt_in_request
)

from app.controllers.api import api_bp
from app.services.booking_service import BookingService
from app.services.payment_service import PaymentService


def get_authenticated_customer_id():

    verify_jwt_in_request()

    claims = get_jwt()

    if claims.get("role") != "CUSTOMER":
        raise PermissionError(
            "Customer access required"
        )

    try:
        return int(
            get_jwt_identity()
        )

    except (TypeError, ValueError):

        raise PermissionError(
            "Invalid user identity"
        )


def serialize_payment(payment):

    return {
        "id": payment.id,

        "booking_id": payment.booking_id,

        "transaction_reference": (
            payment.transaction_reference
        ),

        "amount": float(
            payment.amount
        ),

        "payment_method": (
            payment.payment_method
        ),

        "status": payment.status,

        "paid_at": (
            payment.paid_at.isoformat()
            if payment.paid_at
            else None
        ),

        "created_at": (
            payment.created_at.isoformat()
            if payment.created_at
            else None
        )
    }


@api_bp.route(
    "/bookings/<int:booking_id>/payment",
    methods=["POST"]
)
def create_payment(booking_id):

    try:

        user_id = (
            get_authenticated_customer_id()
        )

        booking = BookingService.get_booking(
            booking_id
        )

        if booking.user_id != user_id:

            return jsonify({
                "status": "error",
                "message": "Booking not found"
            }), 404

        data = request.get_json(
            silent=True
        ) or {}

        payment_method = data.get(
            "payment_method"
        )

        payment = PaymentService.create_payment(
            booking_id=booking_id,
            payment_method=payment_method
        )

        return jsonify({
            "status": "success",
            "message": "Payment initiated",
            "data": serialize_payment(payment)
        }), 201

    except PermissionError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 403

    except ValueError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


@api_bp.route(
    "/bookings/<int:booking_id>/payment/process",
    methods=["POST"]
)
def process_payment(booking_id):

    try:

        user_id = (
            get_authenticated_customer_id()
        )

        booking = BookingService.get_booking(
            booking_id
        )

        if booking.user_id != user_id:

            return jsonify({
                "status": "error",
                "message": "Booking not found"
            }), 404

        data = request.get_json(
            silent=True
        ) or {}

        success = data.get(
            "success",
            True
        )

        if not isinstance(
            success,
            bool
        ):

            return jsonify({
                "status": "error",
                "message": "success must be a boolean"
            }), 400

        payment = PaymentService.process_payment(
            booking_id,
            success
        )

        return jsonify({
            "status": "success",
            "message": (
                "Payment successful"
                if success
                else "Payment failed"
            ),
            "data": {
                "payment": serialize_payment(
                    payment
                ),
                "booking_status": booking.status
            }
        }), 200

    except PermissionError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 403

    except ValueError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400