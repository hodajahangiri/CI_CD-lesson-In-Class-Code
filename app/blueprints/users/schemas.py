# from ...extensions import ma
from app.extensions import ma
from app.models import Users


class UserSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Users #Creates a schema that validates the data as defined by our Users Model

user_schema = UserSchema() # For a single user
users_schema = UserSchema(many=True) # For a list of users
login_schema = UserSchema(exclude=['first_name', 'last_name', 'role'])