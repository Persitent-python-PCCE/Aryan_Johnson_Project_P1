from datetime import date

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    send_file
)

from app.repositories.user_document_repository import (
    UserDocumentRepository
)
from app.repositories.event_poster_repository import (
    EventPosterRepository
)

from app.services.event_service import EventService
from app.services.category_service import CategoryService
from app.services.venue_service import VenueService
from app.services.seat_service import SeatService
from app.services.booking_service import BookingService
from app.utils.auth import role_required
from app.services.file_service import FileService

from app.extensions import db


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

@customer_bp.route("/documents")
@role_required("CUSTOMER")
def documents():

    user_id = session.get("user_id")

    documents = (
        UserDocumentRepository.get_by_user(
            user_id
        )
    )

    return render_template(
        "customer/documents.html",
        documents=documents
    )


@customer_bp.route(
    "/documents/upload",
    methods=["POST"]
)
@role_required("CUSTOMER")
def upload_document():

    user_id = session.get("user_id")

    document_type = request.form.get(
        "document_type",
        ""
    ).strip()

    uploaded_file = request.files.get(
        "file"
    )

    if not uploaded_file:
        flash(
            "Please select a document file.",
            "error"
        )

        return redirect(
            url_for("customer.documents")
        )

    if not uploaded_file.filename:
        flash(
            "Filename is required.",
            "error"
        )

        return redirect(
            url_for("customer.documents")
        )

    try:

        uploaded_file.stream.seek(0)

        file_size = uploaded_file.stream.seek(
            0,
            2
        )

        uploaded_file.stream.seek(0)

        document = FileService.save_document(
            user_id=user_id,
            document_type=document_type,
            filename=uploaded_file.filename,
            file_size=file_size,
            mime_type=uploaded_file.mimetype,
            file_object=uploaded_file
        )

        db.session.commit()

        flash(
            "Document uploaded successfully.",
            "success"
        )

    except ValueError as exc:

        db.session.rollback()

        flash(
            str(exc),
            "error"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to upload document.",
            "error"
        )

    return redirect(
        url_for("customer.documents")
    )


@customer_bp.route(
    "/documents/<int:document_id>/view"
)
@role_required("CUSTOMER")
def view_document(document_id):

    user_id = session.get("user_id")

    document = (
        UserDocumentRepository.get_by_id(
            document_id
        )
    )

    if not document:
        flash(
            "Document not found.",
            "error"
        )

        return redirect(
            url_for("customer.documents")
        )

    if document.user_id != user_id:
        flash(
            "You are not authorized to view this document.",
            "error"
        )

        return redirect(
            url_for("customer.documents")
        )

    from flask import send_file

    return send_file(
        document.file_path,
        mimetype=document.mime_type,
        as_attachment=False,
        download_name=document.original_filename
    )


@customer_bp.route(
    "/documents/<int:document_id>/delete",
    methods=["POST"]
)
@role_required("CUSTOMER")
def delete_document(document_id):

    user_id = session.get("user_id")

    document = (
        UserDocumentRepository.get_by_id(
            document_id
        )
    )

    if not document:
        flash(
            "Document not found.",
            "error"
        )

        return redirect(
            url_for("customer.documents")
        )

    if document.user_id != user_id:
        flash(
            "You are not authorized to delete this document.",
            "error"
        )

        return redirect(
            url_for("customer.documents")
        )

    try:

        FileService.delete_file(
            document.file_path
        )

        UserDocumentRepository.delete(
            document
        )

        db.session.commit()

        flash(
            "Document deleted successfully.",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to delete document.",
            "error"
        )

    return redirect(
        url_for("customer.documents")
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

    # Calculate seat availability for every event
    seat_summary = {}

    for event in events.items:
        seat_summary[event.id] = (
            SeatService.get_event_seat_summary(
                event.id
            )
        )

    return render_template(
        "customer/events.html",
        events=events,
        categories=categories,
        venues=venues,
        keyword=keyword,
        selected_category=category_id,
        selected_venue=venue_id,
        selected_date=event_date,
        seat_summary=seat_summary
    )


@customer_bp.route(
    "/events/<int:event_id>"
)
@role_required("CUSTOMER")
def event_details(event_id):

    event = EventService.get_event(
        event_id
    )

    return render_template(
        "customer/event_details.html",
        event=event
    )

@customer_bp.route(
    "/events/<int:event_id>/poster"
)
@role_required("CUSTOMER")
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

    # Latest uploaded poster
    poster = posters[0]

    if not poster.file_path:
        return (
            "Poster file not found",
            404
        )

    return send_file(
        poster.file_path,
        mimetype=poster.mime_type
    )


@customer_bp.route(
    "/events/<int:event_id>/seats"
)
@role_required("CUSTOMER")
def event_seats(event_id):

    event = EventService.get_event(
        event_id
    )

    if event.status != "PUBLISHED":
        return (
            "This event is not available for booking",
            400
        )

    seats = SeatService.get_available_seats(
        event_id
    )

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

    seat_ids = request.form.getlist(
        "seat_ids"
    )

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