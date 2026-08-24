from datetime import date, time

from flask import jsonify, request

from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    verify_jwt_in_request
)

from app.controllers.api import api_bp
from app.extensions import db

from app.services.category_service import CategoryService
from app.services.venue_service import VenueService
from app.services.event_service import EventService


def require_admin():
    """
    Require a valid JWT belonging to an ADMIN user.
    """

    verify_jwt_in_request()

    identity = get_jwt_identity()
    claims = get_jwt()

    try:
        int(identity)
    except (TypeError, ValueError):
        return (
            jsonify({
                "status": "error",
                "message": "Invalid user identity"
            }),
            401
        )

    if claims.get("role") != "ADMIN":
        return (
            jsonify({
                "status": "error",
                "message": "Admin access required"
            }),
            403
        )

    return None


def serialize_category(category):
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "is_active": category.is_active
    }


def serialize_venue(venue):
    return {
        "id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "city": venue.city,
        "capacity": venue.capacity,
        "description": venue.description
    }


def serialize_event(event):
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "event_date": (
            event.event_date.isoformat()
            if event.event_date
            else None
        ),
        "start_time": (
            event.start_time.isoformat()
            if event.start_time
            else None
        ),
        "end_time": (
            event.end_time.isoformat()
            if event.end_time
            else None
        ),
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


# ============================================================
# CATEGORY API
# ============================================================


@api_bp.route(
    "/admin/categories",
    methods=["GET"]
)
def admin_get_categories():

    auth_error = require_admin()

    if auth_error:
        return auth_error

    categories = CategoryService.get_categories()

    return jsonify({
        "status": "success",
        "data": [
            serialize_category(category)
            for category in categories
        ]
    }), 200


@api_bp.route(
    "/admin/categories",
    methods=["POST"]
)
def admin_create_category():

    auth_error = require_admin()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON"
        }), 400

    name = data.get("name", "")
    description = data.get("description")

    if not isinstance(name, str):
        return jsonify({
            "status": "error",
            "message": "Name must be a string"
        }), 400

    name = name.strip()

    if not name:
        return jsonify({
            "status": "error",
            "message": "Name is required"
        }), 400

    try:

        category = CategoryService.create_category(
            name=name,
            description=description
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Category created successfully",
            "data": serialize_category(category)
        }), 201

    except ValueError as exc:

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


@api_bp.route(
    "/admin/categories/<int:category_id>",
    methods=["GET"]
)
def admin_get_category(category_id):

    auth_error = require_admin()

    if auth_error:
        return auth_error

    try:

        category = CategoryService.get_category(
            category_id
        )

        return jsonify({
            "status": "success",
            "data": serialize_category(category)
        }), 200

    except ValueError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 404


@api_bp.route(
    "/admin/categories/<int:category_id>",
    methods=["PUT"]
)
def admin_update_category(category_id):

    auth_error = require_admin()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON"
        }), 400

    allowed_fields = {
        "name",
        "description",
        "is_active"
    }

    update_data = {
        key: value
        for key, value in data.items()
        if key in allowed_fields
    }

    if "name" in update_data:

        if not isinstance(
            update_data["name"],
            str
        ):
            return jsonify({
                "status": "error",
                "message": "Name must be a string"
            }), 400

        update_data["name"] = (
            update_data["name"].strip()
        )

        if not update_data["name"]:
            return jsonify({
                "status": "error",
                "message": "Name is required"
            }), 400

    if not update_data:
        return jsonify({
            "status": "error",
            "message": "No valid fields provided"
        }), 400

    try:

        category = CategoryService.update_category(
            category_id,
            **update_data
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Category updated successfully",
            "data": serialize_category(category)
        }), 200

    except ValueError as exc:

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


@api_bp.route(
    "/admin/categories/<int:category_id>",
    methods=["DELETE"]
)
def admin_delete_category(category_id):

    auth_error = require_admin()

    if auth_error:
        return auth_error

    try:

        CategoryService.delete_category(
            category_id
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Category deleted successfully"
        }), 200

    except ValueError as exc:

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 404


# ============================================================
# VENUE API
# ============================================================


@api_bp.route(
    "/admin/venues",
    methods=["GET"]
)
def admin_get_venues():

    auth_error = require_admin()

    if auth_error:
        return auth_error

    venues = VenueService.get_venues()

    return jsonify({
        "status": "success",
        "data": [
            serialize_venue(venue)
            for venue in venues
        ]
    }), 200


@api_bp.route(
    "/admin/venues",
    methods=["POST"]
)
def admin_create_venue():

    auth_error = require_admin()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON"
        }), 400

    try:

        name = data.get("name", "")
        address = data.get("address", "")
        city = data.get("city", "")

        if not isinstance(name, str):
            raise ValueError("Name must be a string")

        if not isinstance(address, str):
            raise ValueError("Address must be a string")

        if not isinstance(city, str):
            raise ValueError("City must be a string")

        name = name.strip()
        address = address.strip()
        city = city.strip()

        if not name:
            raise ValueError("Name is required")

        if not address:
            raise ValueError("Address is required")

        if not city:
            raise ValueError("City is required")

        if "capacity" not in data:
            raise ValueError("Capacity is required")

        capacity = int(data["capacity"])

        venue = VenueService.create_venue(
            name=name,
            address=address,
            city=city,
            capacity=capacity,
            description=data.get("description")
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Venue created successfully",
            "data": serialize_venue(venue)
        }), 201

    except (ValueError, TypeError) as exc:

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


@api_bp.route(
    "/admin/venues/<int:venue_id>",
    methods=["GET"]
)
def admin_get_venue(venue_id):

    auth_error = require_admin()

    if auth_error:
        return auth_error

    try:

        venue = VenueService.get_venue(
            venue_id
        )

        return jsonify({
            "status": "success",
            "data": serialize_venue(venue)
        }), 200

    except ValueError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 404


@api_bp.route(
    "/admin/venues/<int:venue_id>",
    methods=["PUT"]
)
def admin_update_venue(venue_id):

    auth_error = require_admin()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON"
        }), 400

    allowed_fields = {
        "name",
        "address",
        "city",
        "capacity",
        "description"
    }

    update_data = {
        key: value
        for key, value in data.items()
        if key in allowed_fields
    }

    for field in (
        "name",
        "address",
        "city"
    ):
        if field in update_data:

            if not isinstance(
                update_data[field],
                str
            ):
                return jsonify({
                    "status": "error",
                    "message": f"{field} must be a string"
                }), 400

            update_data[field] = (
                update_data[field].strip()
            )

    if "capacity" in update_data:

        try:
            update_data["capacity"] = int(
                update_data["capacity"]
            )
        except (ValueError, TypeError):

            return jsonify({
                "status": "error",
                "message": "Capacity must be an integer"
            }), 400

    if not update_data:
        return jsonify({
            "status": "error",
            "message": "No valid fields provided"
        }), 400

    try:

        venue = VenueService.update_venue(
            venue_id,
            **update_data
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Venue updated successfully",
            "data": serialize_venue(venue)
        }), 200

    except ValueError as exc:

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


@api_bp.route(
    "/admin/venues/<int:venue_id>",
    methods=["DELETE"]
)
def admin_delete_venue(venue_id):

    auth_error = require_admin()

    if auth_error:
        return auth_error

    try:

        VenueService.delete_venue(
            venue_id
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Venue deleted successfully"
        }), 200

    except ValueError as exc:

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 404


# ============================================================
# EVENT API
# ============================================================


@api_bp.route(
    "/admin/events",
    methods=["GET"]
)
def admin_get_events():

    auth_error = require_admin()

    if auth_error:
        return auth_error

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

    keyword = request.args.get(
        "keyword"
    )

    category_id = request.args.get(
        "category_id",
        type=int
    )

    venue_id = request.args.get(
        "venue_id",
        type=int
    )

    event_date_string = request.args.get(
        "event_date"
    )

    event_date = None

    if event_date_string:

        try:
            event_date = date.fromisoformat(
                event_date_string
            )
        except ValueError:

            return jsonify({
                "status": "error",
                "message": "Invalid event_date format. Use YYYY-MM-DD"
            }), 400

    status = request.args.get(
        "status"
    )

    result = EventService.search_events(
        keyword=keyword,
        category_id=category_id,
        venue_id=venue_id,
        event_date=event_date,
        status=status,
        page=page,
        per_page=per_page
    )

    return jsonify({
        "status": "success",
        "data": [
            serialize_event(event)
            for event in result.items
        ],
        "pagination": {
            "page": result.page,
            "per_page": result.per_page,
            "pages": result.pages,
            "total": result.total,
            "has_next": result.has_next,
            "has_prev": result.has_prev
        }
    }), 200


@api_bp.route(
    "/admin/events",
    methods=["POST"]
)
def admin_create_event():

    auth_error = require_admin()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON"
        }), 400

    try:

        required_fields = [
            "category_id",
            "venue_id",
            "name",
            "event_date",
            "start_time",
            "end_time"
        ]

        for field in required_fields:

            if field not in data:
                raise ValueError(
                    f"{field} is required"
                )

        event = EventService.create_event(
            category_id=int(
                data["category_id"]
            ),
            venue_id=int(
                data["venue_id"]
            ),
            name=data["name"],
            description=data.get(
                "description"
            ),
            event_date=date.fromisoformat(
                data["event_date"]
            ),
            start_time=time.fromisoformat(
                data["start_time"]
            ),
            end_time=time.fromisoformat(
                data["end_time"]
            ),
            status=data.get(
                "status",
                "DRAFT"
            )
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Event created successfully",
            "data": serialize_event(event)
        }), 201

    except (ValueError, TypeError) as exc:

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


@api_bp.route(
    "/admin/events/<int:event_id>",
    methods=["GET"]
)
def admin_get_event(event_id):

    auth_error = require_admin()

    if auth_error:
        return auth_error

    try:

        event = EventService.get_event(
            event_id
        )

        return jsonify({
            "status": "success",
            "data": serialize_event(event)
        }), 200

    except ValueError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 404


@api_bp.route(
    "/admin/events/<int:event_id>",
    methods=["PUT"]
)
def admin_update_event(event_id):

    auth_error = require_admin()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON"
        }), 400

    try:

        required_fields = [
            "category_id",
            "venue_id",
            "name",
            "event_date",
            "start_time",
            "end_time",
            "status"
        ]

        for field in required_fields:

            if field not in data:
                raise ValueError(
                    f"{field} is required"
                )

        event = EventService.update_event(
            event_id=event_id,
            category_id=int(
                data["category_id"]
            ),
            venue_id=int(
                data["venue_id"]
            ),
            name=data["name"],
            description=data.get(
                "description"
            ),
            event_date=date.fromisoformat(
                data["event_date"]
            ),
            start_time=time.fromisoformat(
                data["start_time"]
            ),
            end_time=time.fromisoformat(
                data["end_time"]
            ),
            status=data["status"]
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Event updated successfully",
            "data": serialize_event(event)
        }), 200

    except (ValueError, TypeError) as exc:

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400


@api_bp.route(
    "/admin/events/<int:event_id>",
    methods=["DELETE"]
)
def admin_delete_event(event_id):

    auth_error = require_admin()

    if auth_error:
        return auth_error

    try:

        EventService.delete_event(
            event_id
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Event deleted successfully"
        }), 200

    except ValueError as exc:

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400