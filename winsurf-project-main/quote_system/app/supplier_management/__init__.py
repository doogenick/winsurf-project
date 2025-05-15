from flask import Blueprint

bp = Blueprint('supplier_management', __name__)

from . import routes
