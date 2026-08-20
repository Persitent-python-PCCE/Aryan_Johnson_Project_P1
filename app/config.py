import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(
    os.getcwd(),
    "uploads"
    )

    POSTER_UPLOAD_FOLDER = os.path.join(
    UPLOAD_FOLDER,
    "posters"
    )

    DOCUMENT_UPLOAD_FOLDER = os.path.join(
    UPLOAD_FOLDER,
    "documents"
    )