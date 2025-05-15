from flask import Blueprint

bp = Blueprint('quote_wizard', __name__, url_prefix='/quote-wizard')

from quote_system.app.quote_wizard import routes
