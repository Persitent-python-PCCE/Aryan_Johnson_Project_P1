from decimal import Decimal

from app import create_app
from app.extensions import db
from app.services.seat_service import SeatService


app = create_app()


with app.app_context():

    VENUE_ID = 2

    seats = []

    # Rows 1-3: VIP
    for row in range(1, 4):
        for seat_number in range(1, 6):
            seats.append({
                "venue_id": VENUE_ID,
                "seat_number": f"R{row}-S{seat_number}",
                "row_number": row,
                "seat_type": "VIP",
                "price": Decimal("1500.00")
            })

    # Rows 4-6: PREMIUM
    for row in range(4, 7):
        for seat_number in range(1, 6):
            seats.append({
                "venue_id": VENUE_ID,
                "seat_number": f"R{row}-S{seat_number}",
                "row_number": row,
                "seat_type": "PREMIUM",
                "price": Decimal("1000.00")
            })

    # Create seats
    created = 0

    for seat_data in seats:

        try:
            SeatService.create_seat(
                venue_id=seat_data["venue_id"],
                seat_number=seat_data["seat_number"],
                row_number=seat_data["row_number"],
                seat_type=seat_data["seat_type"],
                price=seat_data["price"]
            )

            created += 1

        except ValueError as exc:
            print(
                f"Skipping {seat_data['seat_number']}: {exc}"
            )

    db.session.commit()

    print(
        f"Seat seeding completed. "
        f"{created} seat(s) created."
    )