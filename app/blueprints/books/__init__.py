from flask import Blueprint

books_bp = Blueprint('books_bp', __name__)

# It has to be here after creating blueprint
from . import routes