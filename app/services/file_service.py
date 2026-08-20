import os
import uuid

from werkzeug.utils import secure_filename

from app.config import Config
from app.repositories.event_poster_repository import EventPosterRepository
from app.repositories.event_repository import EventRepository
from app.repositories.user_document_repository import UserDocumentRepository
from app.repositories.user_repository import UserRepository


class FileService:

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    POSTER_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "webp"
    }

    DOCUMENT_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "pdf"
    }

    POSTER_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    DOCUMENT_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "application/pdf"
    }

    @staticmethod
    def _get_extension(filename):
        if not filename or "." not in filename:
            return ""

        return filename.rsplit(".", 1)[1].lower()

    @staticmethod
    def _validate_filename(filename):
        if not filename:
            raise ValueError("Filename is required")

        sanitized_filename = secure_filename(filename)

        if not sanitized_filename:
            raise ValueError("Invalid filename")

        return sanitized_filename

    @staticmethod
    def _validate_file_size(file_size):
        if file_size <= 0:
            raise ValueError("File cannot be empty")

        if file_size > FileService.MAX_FILE_SIZE:
            raise ValueError(
                "File size exceeds maximum limit"
            )

    @staticmethod
    def _validate_file_type(
        filename,
        mime_type,
        allowed_extensions,
        allowed_mime_types
    ):
        extension = FileService._get_extension(filename)

        if extension not in allowed_extensions:
            raise ValueError(
                "Unsupported file extension"
            )

        if mime_type not in allowed_mime_types:
            raise ValueError(
                "Unsupported MIME type"
            )

    @staticmethod
    def _generate_stored_filename(extension):
        return f"{uuid.uuid4().hex}.{extension}"

    @staticmethod
    def _ensure_directory(directory):
        os.makedirs(
            directory,
            exist_ok=True
        )

    @staticmethod
    def validate_poster(
        filename,
        file_size,
        mime_type
    ):
        filename = FileService._validate_filename(
            filename
        )

        FileService._validate_file_size(
            file_size
        )

        FileService._validate_file_type(
            filename,
            mime_type,
            FileService.POSTER_EXTENSIONS,
            FileService.POSTER_MIME_TYPES
        )

        return filename

    @staticmethod
    def validate_document(
        filename,
        file_size,
        mime_type
    ):
        filename = FileService._validate_filename(
            filename
        )

        FileService._validate_file_size(
            file_size
        )

        FileService._validate_file_type(
            filename,
            mime_type,
            FileService.DOCUMENT_EXTENSIONS,
            FileService.DOCUMENT_MIME_TYPES
        )

        return filename

    @staticmethod
    def save_poster(
        event_id,
        filename,
        file_size,
        mime_type,
        file_object
    ):
        event = EventRepository.get_by_id(event_id)

        if not event:
            raise ValueError("Event not found")

        filename = FileService.validate_poster(
            filename,
            file_size,
            mime_type
        )

        extension = FileService._get_extension(
            filename
        )

        stored_filename = (
            FileService._generate_stored_filename(
                extension
            )
        )

        directory = Config.POSTER_UPLOAD_FOLDER

        FileService._ensure_directory(
            directory
        )

        file_path = os.path.join(
            directory,
            stored_filename
        )

        file_object.save(file_path)

        try:
            poster = EventPosterRepository.create(
                event_id=event_id,
                original_filename=filename,
                stored_filename=stored_filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type
            )

            return poster

        except Exception:
            FileService.delete_file(file_path)
            raise

    @staticmethod
    def save_document(
        user_id,
        document_type,
        filename,
        file_size,
        mime_type,
        file_object
    ):
        user = UserRepository.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        if not document_type:
            raise ValueError(
                "Document type is required"
            )

        filename = FileService.validate_document(
            filename,
            file_size,
            mime_type
        )

        extension = FileService._get_extension(
            filename
        )

        stored_filename = (
            FileService._generate_stored_filename(
                extension
            )
        )

        directory = Config.DOCUMENT_UPLOAD_FOLDER

        FileService._ensure_directory(
            directory
        )

        file_path = os.path.join(
            directory,
            stored_filename
        )

        file_object.save(file_path)

        try:
            document = UserDocumentRepository.create(
                user_id=user_id,
                document_type=document_type,
                original_filename=filename,
                stored_filename=stored_filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type
            )

            return document

        except Exception:
            FileService.delete_file(file_path)
            raise

    @staticmethod
    def delete_file(file_path):
        if file_path and os.path.exists(file_path):
            os.remove(file_path)