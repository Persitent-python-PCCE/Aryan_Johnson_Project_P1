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

    # JWT Configuration

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        SECRET_KEY
    )

    JWT_TOKEN_LOCATION = ["cookies"]

    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"

    JWT_REFRESH_COOKIE_NAME = "refresh_token_cookie"

    JWT_COOKIE_SECURE = False

    JWT_COOKIE_CSRF_PROTECT = True

    JWT_CSRF_IN_COOKIES = True

    JWT_ACCESS_TOKEN_EXPIRES = 900

    JWT_REFRESH_TOKEN_EXPIRES = 604800