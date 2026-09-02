import os
from datetime import datetime

from sqlalchemy import text

from app import create_app
from app.extensions import db


POSTERS = {
    1: "Rhythm.jpg",
    2: "Laughriot.jpg",
    3: "coastalfootball.jpg",
    4: "lastact.jpg",
    5: "futuretech.jpg",
    6: "diwali.jpg",
    7: "startupconnect.jpg",
    8: "indiemusic.jpg",
    9: "comdedyunderground.png",
    10: "champions.jpg",
    11: "digitalindia.webp",
    12: "winter.jpg",
}


POSTER_DIRECTORY = "/app/uploads/posters"


MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def map_posters():

    app = create_app()

    with app.app_context():

        # Prevent accidental duplicate mappings
        existing_count = db.session.execute(
            text("SELECT COUNT(*) FROM event_posters")
        ).scalar()

        if existing_count > 0:
            raise RuntimeError(
                f"event_posters already contains {existing_count} record(s). "
                "Aborting to prevent duplicates."
            )

        for event_id, filename in POSTERS.items():

            file_path = os.path.join(
                POSTER_DIRECTORY,
                filename
            )

            # Verify the physical file exists
            if not os.path.isfile(file_path):
                raise FileNotFoundError(
                    f"Poster not found: {file_path}"
                )

            # Verify the event exists
            event = db.session.execute(
                text(
                    """
                    SELECT id, name
                    FROM events
                    WHERE id = :event_id
                    """
                ),
                {
                    "event_id": event_id
                }
            ).fetchone()

            if not event:
                raise ValueError(
                    f"Event {event_id} does not exist"
                )

            file_size = os.path.getsize(file_path)

            extension = os.path.splitext(
                filename
            )[1].lower()

            mime_type = MIME_TYPES.get(extension)

            if not mime_type:
                raise ValueError(
                    f"Unsupported file type: {filename}"
                )

            db.session.execute(
                text(
                    """
                    INSERT INTO event_posters
                    (
                        event_id,
                        original_filename,
                        stored_filename,
                        file_path,
                        file_size,
                        mime_type,
                        uploaded_at
                    )
                    VALUES
                    (
                        :event_id,
                        :original_filename,
                        :stored_filename,
                        :file_path,
                        :file_size,
                        :mime_type,
                        :uploaded_at
                    )
                    """
                ),
                {
                    "event_id": event_id,
                    "original_filename": filename,
                    "stored_filename": filename,
                    "file_path": file_path,
                    "file_size": file_size,
                    "mime_type": mime_type,
                    "uploaded_at": datetime.now(),
                }
            )

            print(
                f"Mapped event {event_id} ({event[1]}) -> {filename}"
            )

        db.session.commit()

        print()
        print("SUCCESS: All 12 posters mapped.")


if __name__ == "__main__":
    map_posters()