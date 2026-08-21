from datetime import date

from flask import jsonify, request

from app.controllers.api import api_bp
from app.services.event_service import EventService


def serialize_event(event):
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "event_date": event.event_date.isoformat(),
        "start_time": event.start_time.isoformat(),
        "end_time": event.end_time.isoformat(),
        "status": event.status,
        "category": {
            "id": event.category.id,
            "name": event.category.name
        },
        "venue": {
            "id": event.venue.id,
            "name": event.venue.name,
            "city": event.venue.city
        }
    }


@api_bp.route(
    "/events",
    methods=["GET"]
)
def get_events():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    category_id = request.args.get(
        "category_id",
        type=int
    )

    venue_id = request.args.get(
        "venue_id",
        type=int
    )

    event_date_value = request.args.get(
        "event_date"
    )

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = request.args.get(
        "per_page",
        10,
        type=int
    )

    if page < 1:
        return jsonify({
            "status": "error",
            "message": "Page must be greater than zero"
        }), 400

    if per_page < 1 or per_page > 100:
        return jsonify({
            "status": "error",
            "message": "per_page must be between 1 and 100"
        }), 400

    parsed_date = None

    if event_date_value:
        try:
            parsed_date = date.fromisoformat(
                event_date_value
            )
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Invalid event_date format. Use YYYY-MM-DD"
            }), 400

    events = EventService.search_events(
        keyword=keyword or None,
        category_id=category_id,
        venue_id=venue_id,
        event_date=parsed_date,
        status="PUBLISHED",
        page=page,
        per_page=per_page
    )

    return jsonify({
        "status": "success",
        "data": [
            serialize_event(event)
            for event in events.items
        ],
        "pagination": {
            "page": events.page,
            "per_page": events.per_page,
            "total": events.total,
            "pages": events.pages,
            "has_next": events.has_next,
            "has_previous": events.has_prev
        }
    }), 200


@api_bp.route(
    "/events/<int:event_id>",
    methods=["GET"]
)
def get_event(event_id):

    try:
        event = EventService.get_event(
            event_id
        )

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Event not found"
        }), 404

    if event.status != "PUBLISHED":
        return jsonify({
            "status": "error",
            "message": "Event not found"
        }), 404

    return jsonify({
        "status": "success",
        "data": serialize_event(event)
    }), 200