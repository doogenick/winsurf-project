from flask import Blueprint

bp = Blueprint('booking_system', __name__)

from . import routes
