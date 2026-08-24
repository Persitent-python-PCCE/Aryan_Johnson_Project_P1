from flask import (
    jsonify,
    request,
    send_file
)

from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    verify_jwt_in_request
)

from app.controllers.api import api_bp
from app.repositories.user_document_repository import (
    UserDocumentRepository
)
from app.services.file_service import FileService


def get_authenticated_user_id():

    verify_jwt_in_request()

    identity = get_jwt_identity()

    claims = get_jwt()

    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return None

    if not user_id:
        return None

    return user_id


def serialize_document(document):

    return {
        "id": document.id,
        "document_type": document.document_type,
        "original_filename": document.original_filename,
        "stored_filename": document.stored_filename,
        "file_size": document.file_size,
        "mime_type": document.mime_type,
        "uploaded_at": (
            document.uploaded_at.isoformat()
            if document.uploaded_at
            else None
        )
    }


@api_bp.route(
    "/documents",
    methods=["POST"]
)
def upload_document():

    try:
        user_id = get_authenticated_user_id()

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Invalid user identity"
        }), 401

    document_type = request.form.get(
        "document_type",
        ""
    ).strip()

    uploaded_file = request.files.get(
        "file"
    )

    if not uploaded_file:
        return jsonify({
            "status": "error",
            "message": "Document file is required"
        }), 400

    if not uploaded_file.filename:
        return jsonify({
            "status": "error",
            "message": "Filename is required"
        }), 400

    try:

        uploaded_file.stream.seek(0)

        file_size = (
            uploaded_file.stream.seek(
                0,
                2
            )
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

        from app.extensions import db

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Document uploaded successfully",
            "data": serialize_document(document)
        }), 201

    except ValueError as exc:

        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 400

    except Exception:

        from app.extensions import db

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Unable to upload document"
        }), 500


@api_bp.route(
    "/documents",
    methods=["GET"]
)
def get_documents():

    try:
        user_id = get_authenticated_user_id()

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Invalid user identity"
        }), 401

    documents = (
        UserDocumentRepository.get_by_user(
            user_id
        )
    )

    return jsonify({
        "status": "success",
        "data": [
            serialize_document(document)
            for document in documents
        ]
    }), 200


@api_bp.route(
    "/documents/<int:document_id>",
    methods=["GET"]
)
def get_document(document_id):

    try:
        user_id = get_authenticated_user_id()

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Invalid user identity"
        }), 401

    document = (
        UserDocumentRepository.get_by_id(
            document_id
        )
    )

    if not document:
        return jsonify({
            "status": "error",
            "message": "Document not found"
        }), 404

    if document.user_id != user_id:
        return jsonify({
            "status": "error",
            "message": "Document not found"
        }), 404

    try:

        return send_file(
            document.file_path,
            mimetype=document.mime_type,
            download_name=document.original_filename
        )

    except FileNotFoundError:

        return jsonify({
            "status": "error",
            "message": "Document file not found"
        }), 404


@api_bp.route(
    "/documents/<int:document_id>",
    methods=["DELETE"]
)
def delete_document(document_id):

    try:
        user_id = get_authenticated_user_id()

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Invalid user identity"
        }), 401

    document = (
        UserDocumentRepository.get_by_id(
            document_id
        )
    )

    if not document:
        return jsonify({
            "status": "error",
            "message": "Document not found"
        }), 404

    if document.user_id != user_id:
        return jsonify({
            "status": "error",
            "message": "Document not found"
        }), 404

    file_path = document.file_path

    try:

        UserDocumentRepository.delete(
            document
        )

        from app.extensions import db

        db.session.commit()

        FileService.delete_file(
            file_path
        )

        return jsonify({
            "status": "success",
            "message": "Document deleted successfully"
        }), 200

    except Exception:

        from app.extensions import db

        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Unable to delete document"
        }), 500