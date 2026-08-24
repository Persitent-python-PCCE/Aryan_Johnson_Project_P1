import os
import sys
from datetime import date, time

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    PROJECT_ROOT
)


from app import create_app
from app.extensions import db
from app.models import Category, Venue, Seat, Event

# ============================================================
# SEED DATA
# ============================================================

CATEGORIES = [
    {
        "name": "Music",
        "description": "Live concerts, music festivals and performances."
    },
    {
        "name": "Comedy",
        "description": "Stand-up comedy shows and comedy performances."
    },
    {
        "name": "Sports",
        "description": "Live sporting events and competitions."
    },
    {
        "name": "Theatre",
        "description": "Plays, stage productions and theatrical performances."
    },
    {
        "name": "Technology",
        "description": "Technology conferences, expos and developer events."
    },
    {
        "name": "Cultural",
        "description": "Cultural celebrations and traditional performances."
    },
    {
        "name": "Business",
        "description": "Business conferences, networking events and seminars."
    },
    {
        "name": "Entertainment",
        "description": "General entertainment and special events."
    }
]


VENUES = [
    {
        "name": "Mangalore Convention Centre",
        "address": "MG Road",
        "city": "Mangalore",
        "capacity": 120,
        "description": (
            "A modern indoor venue suitable for concerts, conferences "
            "and large-scale cultural events."
        ),
        "rows": 10,
        "seats_per_row": 12
    },
    {
        "name": "Coastal Arena",
        "address": "Kavoor Road",
        "city": "Mangalore",
        "capacity": 160,
        "description": (
            "A versatile arena designed for sports, entertainment "
            "and live performances."
        ),
        "rows": 10,
        "seats_per_row": 16
    },
    {
        "name": "Grand Theatre",
        "address": "Church Street",
        "city": "Bangalore",
        "capacity": 96,
        "description": (
            "A premium theatre with a dedicated stage and tiered "
            "seating for performances."
        ),
        "rows": 8,
        "seats_per_row": 12
    },
    {
        "name": "City Sports Arena",
        "address": "Outer Ring Road",
        "city": "Bangalore",
        "capacity": 180,
        "description": (
            "A large indoor sports and entertainment venue "
            "with excellent spectator seating."
        ),
        "rows": 12,
        "seats_per_row": 15
    },
    {
        "name": "Phoenix Events Hall",
        "address": "Andheri East",
        "city": "Mumbai",
        "capacity": 200,
        "description": (
            "A spacious event hall suitable for conferences, "
            "business events and entertainment."
        ),
        "rows": 10,
        "seats_per_row": 20
    }
]


EVENTS = [
    {
        "name": "Rhythm by the Coast",
        "category": "Music",
        "venue": "Mangalore Convention Centre",
        "description": (
            "An energetic evening of live music featuring "
            "independent artists and contemporary performances."
        ),
        "event_date": date(2026, 9, 15),
        "start_time": time(18, 30),
        "end_time": time(21, 30)
    },
    {
        "name": "Laugh Riot Live",
        "category": "Comedy",
        "venue": "Grand Theatre",
        "description": (
            "A night of stand-up comedy featuring a lineup "
            "of emerging and established comedians."
        ),
        "event_date": date(2026, 9, 20),
        "start_time": time(19, 0),
        "end_time": time(21, 30)
    },
    {
        "name": "Coastal Football Cup",
        "category": "Sports",
        "venue": "Coastal Arena",
        "description": (
            "An exciting live football tournament featuring "
            "top local teams competing for the Coastal Cup."
        ),
        "event_date": date(2026, 9, 27),
        "start_time": time(17, 0),
        "end_time": time(20, 0)
    },
    {
        "name": "The Last Act",
        "category": "Theatre",
        "venue": "Grand Theatre",
        "description": (
            "A dramatic stage production exploring ambition, "
            "friendship and the choices that define us."
        ),
        "event_date": date(2026, 10, 3),
        "start_time": time(18, 30),
        "end_time": time(21, 0)
    },
    {
        "name": "FutureTech India 2026",
        "category": "Technology",
        "venue": "Phoenix Events Hall",
        "description": (
            "A technology conference covering artificial intelligence, "
            "cloud computing, cybersecurity and emerging technologies."
        ),
        "event_date": date(2026, 10, 10),
        "start_time": time(9, 30),
        "end_time": time(17, 30)
    },
    {
        "name": "Diwali Cultural Evening",
        "category": "Cultural",
        "venue": "Mangalore Convention Centre",
        "description": (
            "A colourful cultural celebration featuring music, "
            "dance and traditional performances."
        ),
        "event_date": date(2026, 10, 24),
        "start_time": time(17, 30),
        "end_time": time(21, 0)
    },
    {
        "name": "Startup Connect 2026",
        "category": "Business",
        "venue": "Phoenix Events Hall",
        "description": (
            "A networking and knowledge-sharing event connecting "
            "entrepreneurs, investors and technology professionals."
        ),
        "event_date": date(2026, 11, 7),
        "start_time": time(10, 0),
        "end_time": time(17, 0)
    },
    {
        "name": "Indie Music Nights",
        "category": "Music",
        "venue": "City Sports Arena",
        "description": (
            "A multi-artist live music experience celebrating "
            "independent musicians and emerging talent."
        ),
        "event_date": date(2026, 11, 14),
        "start_time": time(18, 0),
        "end_time": time(22, 0)
    },
    {
        "name": "Comedy Underground",
        "category": "Comedy",
        "venue": "Mangalore Convention Centre",
        "description": (
            "A relaxed evening of stand-up comedy featuring "
            "fresh voices from the Indian comedy circuit."
        ),
        "event_date": date(2026, 11, 21),
        "start_time": time(19, 0),
        "end_time": time(21, 30)
    },
    {
        "name": "Champions Indoor League",
        "category": "Sports",
        "venue": "City Sports Arena",
        "description": (
            "A fast-paced indoor sports championship designed "
            "for an exciting live spectator experience."
        ),
        "event_date": date(2026, 11, 28),
        "start_time": time(16, 0),
        "end_time": time(20, 0)
    },
    {
        "name": "Digital India Business Summit",
        "category": "Business",
        "venue": "Phoenix Events Hall",
        "description": (
            "A business summit focused on digital transformation, "
            "innovation and the future of modern enterprises."
        ),
        "event_date": date(2026, 12, 5),
        "start_time": time(9, 30),
        "end_time": time(16, 30)
    },
    {
        "name": "Winter Entertainment Fest",
        "category": "Entertainment",
        "venue": "Coastal Arena",
        "description": (
            "A large-scale entertainment festival featuring "
            "music, performances and interactive activities."
        ),
        "event_date": date(2026, 12, 19),
        "start_time": time(17, 0),
        "end_time": time(22, 0)
    }
]


# ============================================================
# HELPERS
# ============================================================

def create_categories():
    """
    Create categories if they don't already exist.
    """

    categories = {}

    for data in CATEGORIES:

        category = Category.query.filter_by(
            name=data["name"]
        ).first()

        if not category:

            category = Category(
                name=data["name"],
                description=data["description"],
                is_active=True
            )

            db.session.add(category)

        categories[data["name"]] = category

    db.session.flush()

    return categories


def create_venues():
    """
    Create venues and their physical seat layouts.
    """

    venues = {}

    for data in VENUES:

        venue = Venue.query.filter_by(
            name=data["name"]
        ).first()

        if not venue:

            venue = Venue(
                name=data["name"],
                address=data["address"],
                city=data["city"],
                capacity=data["capacity"],
                description=data["description"]
            )

            db.session.add(venue)
            db.session.flush()

        venues[data["name"]] = venue

        create_seats(
            venue=venue,
            rows=data["rows"],
            seats_per_row=data["seats_per_row"]
        )

    return venues


def create_seats(
    venue,
    rows,
    seats_per_row
):
    """
    Create the physical seats for a venue.

    Seats are only created if the venue currently has
    no seats. This makes the seed operation safe to run
    multiple times.
    """

    existing_seat = Seat.query.filter_by(
        venue_id=venue.id
    ).first()

    if existing_seat:
        return

    for row in range(1, rows + 1):

        for position in range(1, seats_per_row + 1):

            # First two rows = VIP
            if row <= 2:

                seat_type = "VIP"
                price = 2500

            # Next three rows = PREMIUM
            elif row <= 5:

                seat_type = "PREMIUM"
                price = 1800

            # Remaining rows = REGULAR
            else:

                seat_type = "REGULAR"
                price = 1000

            seat_number = (
                f"{chr(64 + row)}{position}"
            )

            seat = Seat(
                venue_id=venue.id,
                seat_number=seat_number,
                row_number=row,
                seat_type=seat_type,
                price=price,
                is_active=True
            )

            db.session.add(seat)

    db.session.flush()


def create_events(
    categories,
    venues
):
    """
    Create published events.
    """

    created = 0

    for data in EVENTS:

        existing_event = Event.query.filter_by(
            name=data["name"]
        ).first()

        if existing_event:
            continue

        event = Event(
            category_id=categories[
                data["category"]
            ].id,

            venue_id=venues[
                data["venue"]
            ].id,

            name=data["name"],

            description=data[
                "description"
            ],

            event_date=data[
                "event_date"
            ],

            start_time=data[
                "start_time"
            ],

            end_time=data[
                "end_time"
            ],

            status="PUBLISHED"
        )

        db.session.add(event)

        created += 1

    db.session.flush()

    return created


# ============================================================
# MAIN
# ============================================================

def seed_database():

    app = create_app()

    with app.app_context():

        print()
        print("=" * 55)
        print("        TICKET BOOKING - DATABASE SEED")
        print("=" * 55)
        print()

        try:

            # ------------------------------------------------
            # Categories
            # ------------------------------------------------

            categories = create_categories()

            print(
                f"Categories available : "
                f"{len(categories)}"
            )


            # ------------------------------------------------
            # Venues + Seats
            # ------------------------------------------------

            venues = create_venues()

            total_seats = Seat.query.count()

            print(
                f"Venues available     : "
                f"{len(venues)}"
            )

            print(
                f"Seats available      : "
                f"{total_seats}"
            )


            # ------------------------------------------------
            # Events
            # ------------------------------------------------

            events_created = create_events(
                categories,
                venues
            )

            total_events = Event.query.count()

            print(
                f"Events created       : "
                f"{events_created}"
            )

            print(
                f"Total events         : "
                f"{total_events}"
            )


            # ------------------------------------------------
            # Commit
            # ------------------------------------------------

            db.session.commit()

            print()
            print("-" * 55)
            print("Seed completed successfully.")
            print("-" * 55)
            print()

            print(
                "Categories :",
                Category.query.count()
            )

            print(
                "Venues     :",
                Venue.query.count()
            )

            print(
                "Seats      :",
                Seat.query.count()
            )

            print(
                "Events     :",
                Event.query.count()
            )

            print()
            print("=" * 55)


        except Exception as exc:

            db.session.rollback()

            print()
            print("=" * 55)
            print("SEED FAILED")
            print("=" * 55)
            print()
            print(str(exc))
            print()

            raise


if __name__ == "__main__":
    seed_database()