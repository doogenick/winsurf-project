from flask import Blueprint

bp = Blueprint('supplier_management', __name__, template_folder='templates')

# Import routes after creating the blueprint to avoid circular imports
from . import routes
