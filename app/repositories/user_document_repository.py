from app.extensions import db
from app.models.user_document import UserDocument


class UserDocumentRepository:

    @staticmethod
    def create(
        user_id,
        document_type,
        original_filename,
        stored_filename,
        file_path,
        file_size,
        mime_type
    ):
        document = UserDocument(
            user_id=user_id,
            document_type=document_type,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type
        )

        db.session.add(document)
        db.session.flush()

        return document

    @staticmethod
    def get_by_id(document_id):
        return db.session.get(UserDocument, document_id)

    @staticmethod
    def get_by_user(user_id):
        return (
            UserDocument.query
            .filter(
                UserDocument.user_id == user_id
            )
            .order_by(
                UserDocument.uploaded_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_stored_filename(stored_filename):
        return (
            UserDocument.query
            .filter(
                UserDocument.stored_filename == stored_filename
            )
            .first()
        )

    @staticmethod
    def update(document, **kwargs):
        for field, value in kwargs.items():
            if hasattr(document, field):
                setattr(document, field, value)

        db.session.flush()

        return document

    @staticmethod
    def delete(document):
        db.session.delete(document)
        db.session.flush()