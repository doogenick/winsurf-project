from flask import Blueprint

bp = Blueprint('tour_packages', __name__)

from quote_system.app.tour_packages import routes
