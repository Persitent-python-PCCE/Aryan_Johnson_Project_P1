from app.extensions import db
from datetime import date, time
import os

from app.config import Config
from app.services.file_service import FileService
from app.repositories.event_poster_repository import EventPosterRepository

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

@admin_bp.route(
    "/categories/<int:category_id>/delete",
    methods=["POST"]
)
@role_required("ADMIN")
def delete_category(category_id):

    try:

        CategoryService.delete_category(
            category_id
        )

        db.session.commit()

        flash(
            "Category deleted successfully.",
            "success"
        )

    except ValueError as exc:

        db.session.rollback()

        flash(
            str(exc),
            "danger"
        )

    except Exception:

        db.session.rollback()
        raise

    return redirect(
        url_for("admin.categories")
    )


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

@admin_bp.route(
    "/venues/<int:venue_id>/delete",
    methods=["POST"]
)
@role_required("ADMIN")
def delete_venue(venue_id):

    try:

        VenueService.delete_venue(
            venue_id
        )

        db.session.commit()

        flash(
            "Venue deleted successfully.",
            "success"
        )

    except ValueError as exc:

        db.session.rollback()

        flash(
            str(exc),
            "danger"
        )

    except Exception:

        db.session.rollback()
        raise

    return redirect(
        url_for("admin.venues")
    )


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


@admin_bp.route(
    "/events/create",
    methods=["GET", "POST"]
)
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
        ).strip().upper()


        # ----------------------------------------------------
        # Poster
        # ----------------------------------------------------

        poster = request.files.get(
            "poster"
        )


        # ----------------------------------------------------
        # Poster required for published events
        # ----------------------------------------------------

        if status == "PUBLISHED":

            if not poster or not poster.filename:

                raise ValueError(
                    "A poster is required for published events"
                )


        # ----------------------------------------------------
        # Create event
        # ----------------------------------------------------

        event = EventService.create_event(
            category_id=category_id,
            venue_id=venue_id,
            name=name,
            description=description,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            status=status
        )


        # ----------------------------------------------------
        # Save poster
        # ----------------------------------------------------

        if poster and poster.filename:

            poster.stream.seek(0, 2)

            file_size = poster.stream.tell()

            poster.stream.seek(0)

            FileService.save_poster(
                event_id=event.id,
                filename=poster.filename,
                file_size=file_size,
                mime_type=poster.mimetype,
                file_object=poster
            )


        # ----------------------------------------------------
        # Commit event + poster
        # ----------------------------------------------------

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
    "/events/<int:event_id>/delete",
    methods=["POST"]
)
@role_required("ADMIN")
def delete_event(event_id):

    try:

        EventService.delete_event(
            event_id
        )

        db.session.commit()

        flash(
            "Event deleted successfully.",
            "success"
        )

    except ValueError as exc:

        db.session.rollback()

        flash(
            str(exc),
            "danger"
        )

    except Exception:

        db.session.rollback()
        raise

    return redirect(
        url_for("admin.events")
    )


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


@admin_bp.route(
    "/events/<int:event_id>/poster",
    methods=["POST"]
)
@role_required("ADMIN")
def upload_event_poster(event_id):

    try:

        # --------------------------------------------------------
        # Verify event exists
        # --------------------------------------------------------

        event = EventService.get_event(
            event_id
        )

        uploaded_file = request.files.get(
            "poster"
        )

        if not uploaded_file:
            flash(
                "Please select a poster image.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin.edit_event",
                    event_id=event_id
                )
            )

        if not uploaded_file.filename:
            flash(
                "Poster filename is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin.edit_event",
                    event_id=event_id
                )
            )

        # --------------------------------------------------------
        # Calculate file size
        # --------------------------------------------------------

        uploaded_file.stream.seek(0)

        file_size = uploaded_file.stream.seek(
            0,
            2
        )

        uploaded_file.stream.seek(0)

        # --------------------------------------------------------
        # Save poster
        # --------------------------------------------------------

        poster = FileService.save_poster(
            event_id=event_id,
            filename=uploaded_file.filename,
            file_size=file_size,
            mime_type=uploaded_file.mimetype,
            file_object=uploaded_file
        )

        db.session.commit()

        flash(
            "Event poster uploaded successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.edit_event",
                event_id=event_id
            )
        )

    except ValueError as exc:

        db.session.rollback()

        flash(
            str(exc),
            "danger"
        )

        return redirect(
            url_for(
                "admin.edit_event",
                event_id=event_id
            )
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to upload event poster.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.edit_event",
                event_id=event_id
            )
        )


@admin_bp.route(
    "/events/<int:event_id>/poster"
)
@role_required("ADMIN")
def event_poster(event_id):

    event = EventService.get_event(
        event_id
    )

    posters = EventPosterRepository.get_by_event(
        event.id
    )

    if not posters:
        return (
            "Poster not found",
            404
        )

    poster = posters[0]

    if not os.path.exists(poster.file_path):
        return (
            "Poster file not found",
            404
        )

    from flask import send_file

    return send_file(
        poster.file_path,
        mimetype=poster.mime_type
    )


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