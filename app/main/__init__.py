from flask import Blueprint

bp = Blueprint('main', __name__)
bp2 = Blueprint('filters', __name__)

from app.main import routes
from app.main import filters