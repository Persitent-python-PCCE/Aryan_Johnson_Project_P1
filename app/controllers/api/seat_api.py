from flask import jsonify

from app.controllers.api import api_bp
from app.services.event_service import EventService
from app.services.seat_service import SeatService


def serialize_seat(seat):
    return {
        "id": seat.id,
        "seat_number": seat.seat_number,
        "row_number": seat.row_number,
        "seat_type": seat.seat_type,
        "price": float(seat.price)
    }


@api_bp.route(
    "/events/<int:event_id>/seats",
    methods=["GET"]
)
def get_event_seats(event_id):

    try:
        event = EventService.get_event(
            event_id
        )

        if event.status != "PUBLISHED":
            return jsonify({
                "status": "error",
                "message": "Event not found"
            }), 404

        seats = SeatService.get_available_seats(
            event_id
        )

        summary = SeatService.get_event_seat_summary(
            event_id
        )

        return jsonify({
            "status": "success",
            "data": {
                "event_id": event.id,
                "event_name": event.name,
                "total_seats": summary["total"],
                "available_seats": summary["available"],
                "seats": [
                    serialize_seat(seat)
                    for seat in seats
                ]
            }
        }), 200

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Event not found"
        }), 404