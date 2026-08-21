from app.extensions import db
from datetime import date, time

from app.extensions import db

from app.services.event_service import EventService
from app.services.category_service import CategoryService
from app.services.venue_service import VenueService
from app.services.booking_service import BookingService

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from app.services.category_service import CategoryService
from app.services.venue_service import VenueService
from app.services.event_service import EventService
from app.utils.auth import role_required


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


@admin_bp.route("/dashboard")
@role_required("ADMIN")
def dashboard():
    return render_template(
        "admin/dashboard.html"
    )


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@admin_bp.route("/categories")
@role_required("ADMIN")
def categories():
    categories = CategoryService.get_categories()

    return render_template(
        "admin/categories.html",
        categories=categories
    )


@admin_bp.route(
    "/categories/create",
    methods=["GET", "POST"]
)
@role_required("ADMIN")
def create_category():
    if request.method == "GET":
        return render_template(
            "admin/category_form.html"
        )

    name = request.form.get(
        "name",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    try:
        CategoryService.create_category(
            name=name,
            description=description or None
        )

        db.session.commit()

        flash(
            "Category created successfully.",
            "success"
        )

        return redirect(
            url_for("admin.categories")
        )

    except ValueError as exc:
        db.session.rollback()

        flash(
            str(exc),
            "danger"
        )

        return render_template(
            "admin/category_form.html"
        )

    except Exception:
        db.session.rollback()
        raise


# ---------------------------------------------------------------------------
# Venues
# ---------------------------------------------------------------------------

@admin_bp.route("/venues")
@role_required("ADMIN")
def venues():
    venues = VenueService.get_venues()

    return render_template(
        "admin/venues.html",
        venues=venues
    )


@admin_bp.route(
    "/venues/create",
    methods=["GET", "POST"]
)
@role_required("ADMIN")
def create_venue():
    if request.method == "GET":
        return render_template(
            "admin/venue_form.html"
        )

    name = request.form.get(
        "name",
        ""
    ).strip()

    address = request.form.get(
        "address",
        ""
    ).strip()

    city = request.form.get(
        "city",
        ""
    ).strip()

    capacity = request.form.get(
        "capacity",
        ""
    ).strip()

    try:
        capacity = int(capacity)

        VenueService.create_venue(
            name=name,
            address=address,
            city=city,
            capacity=capacity
        )

        db.session.commit()

        flash(
            "Venue created successfully.",
            "success"
        )

        return redirect(
            url_for("admin.venues")
        )

    except ValueError as exc:
        db.session.rollback()

        flash(
            str(exc),
            "danger"
        )

        return render_template(
            "admin/venue_form.html"
        )

    except Exception():
        db.session.rollback()
        raise


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

@admin_bp.route("/events")
@role_required("ADMIN")
def events():
    result = EventService.search_events(
        page=1,
        per_page=100
    )

    return render_template(
        "admin/events.html",
        events=result
    )


@admin_bp.route("/events/create", methods=["GET", "POST"])
@role_required("ADMIN")
def create_event():

    categories = CategoryService.get_categories(
        active_only=True
    )

    venues = VenueService.get_venues()

    if request.method == "GET":
        return render_template(
            "admin/event_form.html",
            categories=categories,
            venues=venues
        )

    try:
        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category_id = int(
            request.form.get("category_id")
        )

        venue_id = int(
            request.form.get("venue_id")
        )

        event_date = date.fromisoformat(
            request.form.get("event_date")
        )

        start_time = time.fromisoformat(
            request.form.get("start_time")
        )

        end_time = time.fromisoformat(
            request.form.get("end_time")
        )

        status = request.form.get(
            "status",
            "DRAFT"
        )

        EventService.create_event(
            category_id=category_id,
            venue_id=venue_id,
            name=name,
            description=description,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            status=status
        )

        db.session.commit()

        flash(
            "Event created successfully.",
            "success"
        )

        return redirect(
            url_for("admin.events")
        )

    except ValueError as exc:

        db.session.rollback()

        flash(
            str(exc),
            "danger"
        )

        return render_template(
            "admin/event_form.html",
            categories=categories,
            venues=venues
        )

    except Exception:

        db.session.rollback()

        raise


@admin_bp.route(
    "/events/<int:event_id>/edit",
    methods=["GET", "POST"]
)
@role_required("ADMIN")
def edit_event(event_id):

    event = EventService.get_event(
        event_id
    )

    categories = CategoryService.get_categories(
        active_only=True
    )

    venues = VenueService.get_venues()

    if request.method == "GET":

        return render_template(
            "admin/event_edit.html",
            event=event,
            categories=categories,
            venues=venues
        )

    try:

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category_id = int(
            request.form.get("category_id")
        )

        venue_id = int(
            request.form.get("venue_id")
        )

        event_date = date.fromisoformat(
            request.form.get("event_date")
        )

        start_time = time.fromisoformat(
            request.form.get("start_time")
        )

        end_time = time.fromisoformat(
            request.form.get("end_time")
        )

        status = request.form.get(
            "status",
            "DRAFT"
        )

        EventService.update_event(
            event_id=event_id,
            category_id=category_id,
            venue_id=venue_id,
            name=name,
            description=description,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            status=status
        )

        db.session.commit()

        flash(
            "Event updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.events")
        )

    except ValueError as exc:

        db.session.rollback()

        flash(
            str(exc),
            "danger"
        )

        return render_template(
            "admin/event_edit.html",
            event=event,
            categories=categories,
            venues=venues
        )

    except Exception:

        db.session.rollback()
        raise


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------

@admin_bp.route("/bookings")
@role_required("ADMIN")
def bookings():

    booking_reference = request.args.get(
        "booking_reference",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int
    )

    bookings = BookingService.search_bookings(
        booking_reference=booking_reference or None,
        status=status or None,
        page=page,
        per_page=10
    )

    return render_template(
        "admin/bookings.html",
        bookings=bookings,
        booking_reference=booking_reference,
        selected_status=status
    )

@admin_bp.route("/bookings/<int:booking_id>")
@role_required("ADMIN")
def booking_details(booking_id):

    try:
        booking = BookingService.get_booking(
            booking_id
        )

        return render_template(
            "admin/booking_details.html",
            booking=booking
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger"
        )

        return redirect(
            url_for("admin.bookings")
        )

@admin_bp.route(
    "/bookings/<int:booking_id>/cancel",
    methods=["POST"]
)
@role_required("ADMIN")
def cancel_booking(booking_id):

    try:

        booking = BookingService.get_booking(
            booking_id
        )

        if booking.status != "CONFIRMED":
            flash(
                "Only confirmed bookings can be cancelled.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin.booking_details",
                    booking_id=booking_id
                )
            )

        BookingService.cancel_booking(
            booking_id
        )

        flash(
            "Booking cancelled successfully.",
            "success"
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger"
        )

    return redirect(
        url_for(
            "admin.booking_details",
            booking_id=booking_id
        )
    )