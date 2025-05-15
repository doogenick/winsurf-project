from flask import Blueprint

bp = Blueprint('quote_management', __name__)

from . import routes
