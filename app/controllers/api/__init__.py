from flask import Blueprint


api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api/v1"
)


from app.controllers.api import health_api
from app.controllers.api import event_api
from app.controllers.api import seat_api
from app.controllers.api import auth_api
from app.controllers.api import booking_api
from app.controllers.api import admin_api
from app.controllers.api import payment_api
from app.controllers.api import document_api