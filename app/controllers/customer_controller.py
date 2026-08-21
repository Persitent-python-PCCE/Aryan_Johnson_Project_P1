from datetime import date

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from app.services.event_service import EventService
from app.services.category_service import CategoryService
from app.services.venue_service import VenueService
from app.services.seat_service import SeatService
from app.services.booking_service import BookingService
from app.services.seat_service import SeatService
from app.utils.auth import role_required


customer_bp = Blueprint(
    "customer",
    __name__,
    url_prefix="/customer"
)


@customer_bp.route("/dashboard")
@role_required("CUSTOMER")
def dashboard():
    return render_template(
        "customer/dashboard.html"
    )


@customer_bp.route("/events")
@role_required("CUSTOMER")
def events():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    category_id = request.args.get(
        "category_id",
        ""
    )

    venue_id = request.args.get(
        "venue_id",
        ""
    )

    event_date = request.args.get(
        "event_date",
        ""
    )

    page = request.args.get(
        "page",
        1,
        type=int
    )

    try:
        category_id = (
            int(category_id)
            if category_id
            else None
        )

        venue_id = (
            int(venue_id)
            if venue_id
            else None
        )

        parsed_date = (
            date.fromisoformat(event_date)
            if event_date
            else None
        )

    except ValueError:

        category_id = None
        venue_id = None
        parsed_date = None

    events = EventService.search_events(
        keyword=keyword or None,
        category_id=category_id,
        venue_id=venue_id,
        event_date=parsed_date,
        status="PUBLISHED",
        page=page,
        per_page=10
    )

    categories = CategoryService.get_categories(
        active_only=True
    )

    venues = VenueService.get_venues()

    return render_template(
        "customer/events.html",
        events=events,
        categories=categories,
        venues=venues,
        keyword=keyword,
        selected_category=category_id,
        selected_venue=venue_id,
        selected_date=event_date
    )


@customer_bp.route("/events/<int:event_id>")
@role_required("CUSTOMER")
def event_details(event_id):

    event = EventService.get_event(
        event_id
    )

    return render_template(
        "customer/event_details.html",
        event=event
    )

@customer_bp.route("/events/<int:event_id>/seats")
@role_required("CUSTOMER")
def event_seats(event_id):

    event = EventService.get_event(event_id)

    if not event:
        return "Event not found", 404

    if event.status != "PUBLISHED":
        return "This event is not available for booking", 400

    seats = SeatService.get_available_seats(
        event_id
    )

    return render_template(
        "customer/event_seats.html",
        event=event,
        seats=seats
    )

@customer_bp.route("/events/<int:event_id>/seats")
@role_required("CUSTOMER")
def event_seats(event_id):

    event = EventService.get_event(event_id)

    if event.status != "PUBLISHED":
        return "This event is not available for booking", 400

    seats = SeatService.get_available_seats(event_id)

    return render_template(
        "customer/event_seats.html",
        event=event,
        seats=seats
    )


@customer_bp.route(
    "/events/<int:event_id>/book",
    methods=["POST"]
)
@role_required("CUSTOMER")
def book_event(event_id):

    user_id = session.get("user_id")

    seat_ids = request.form.getlist("seat_ids")

    try:
        seat_ids = [
            int(seat_id)
            for seat_id in seat_ids
        ]

        booking = BookingService.create_booking(
            user_id=user_id,
            event_id=event_id,
            seat_ids=seat_ids
        )

        return redirect(
            url_for(
                "customer.booking_confirmation",
                booking_id=booking.id
            )
        )

    except ValueError as exc:

        flash(
            str(exc),
            "danger"
        )

        return redirect(
            url_for(
                "customer.event_seats",
                event_id=event_id
            )
        )


@customer_bp.route(
    "/bookings/<int:booking_id>"
)
@role_required("CUSTOMER")
def booking_confirmation(booking_id):

    booking = BookingService.get_booking(
        booking_id
    )

    if booking.user_id != session.get("user_id"):
        return "Unauthorized", 403

    return render_template(
        "customer/booking_confirmation.html",
        booking=booking
    )


@customer_bp.route("/bookings")
@role_required("CUSTOMER")
def bookings():

    user_id = session.get("user_id")

    bookings = BookingService.get_user_bookings(
        user_id
    )

    return render_template(
        "customer/bookings.html",
        bookings=bookings
    )


@customer_bp.route(
    "/bookings/<int:booking_id>/cancel",
    methods=["POST"]
)
@role_required("CUSTOMER")
def cancel_booking(booking_id):

    try:

        booking = BookingService.get_booking(
            booking_id
        )

        if booking.user_id != session.get("user_id"):
            return "Unauthorized", 403

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
        url_for("customer.bookings")
    )