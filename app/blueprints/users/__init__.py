from flask import Blueprint

users_bp = Blueprint('users_bp', __name__)

# It has to be here after creating blueprint
from app.blueprints.users import routes