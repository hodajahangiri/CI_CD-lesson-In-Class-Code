# from ...blueprints.users import users_bd
from app.blueprints.users import users_bp
from .schemas import user_schema, users_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Users,db
from app.extensions import limiter
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import encode_token, token_required


# LOGIN ROUTE
@users_bp.route('/login', methods=['POST'])
@limiter.limit("5 per 10 min")
def login():
  try:
    # get my user credentials - responsibility for my client
    credentials_data = login_schema.load(request.json)
  except ValidationError as e:
    return jsonify(e.messages), 400
  
  user = db.session.query(Users).where(Users.email==credentials_data["email"]).first() #search my db for a user with the email in the request
  if user and check_password_hash(user.password, credentials_data["password"]):
    # Create token for user
    token = encode_token(user.id,role=user.role)
    response = {
      "message" : f"Welcome {user.first_name}",
      "token" : token
    }
    return jsonify(response), 200


# CREATE USERS ROUTE
@users_bp.route("", methods=['POST'])
# @limiter.limit("2 per day")
def create_user():
  try:
    # get my user data - responsibility for my client
    data = user_schema.load(request.json) # JSON - > Python
  except ValidationError as e:
    return jsonify(e.messages), 400 #Returning the error as a response so the client can see whats wrong with the status code
  
  # taken_email = db.session.query(Users).where(Users.email==data["email"]).first()
  # if taken_email:
  #   return jsonify({"message" : f"{data["email"]} is already taken by another user."}), 400
  
  data["password"] = generate_password_hash(data["password"]) #resetting the password key value to the hash of the current password
  try:
    # Create a User object from my user data
    new_user = Users(**data)
    # add User to session
    db.session.add(new_user)
    # commit to session
    db.session.commit()
    # Python - > Python
    return user_schema.jsonify(new_user), 201 #Successful creation status code
  except:
    return jsonify({"message" : f"{data["email"]} is already taken by another user."}), 400

# READ USERS ROUTE
@users_bp.route("", methods=["GET"]) #Endpoint to get user information
@limiter.limit("5 per hour")
def read_users():
  users = db.session.query(Users).all()
  return users_schema.jsonify(users), 200 # Returns the ist of users and the response 200

#Read Individual User - using a Dynamic Endpoint
@users_bp.route("/profile", methods=["GET"])
@limiter.limit("15 per hour")
@token_required
def read_user():
  user_id = request.logged_in_user_id
  user = db.session.get(Users, user_id)
  return user_schema.jsonify(user), 200

@users_bp.route("", methods=["DELETE"])
@token_required
def delete_user():
  token_id = request.logged_in_user_id
  user = db.session.get(Users, token_id) #look up whoever the token belongs to (who is logged in )
  if not user:
    return jsonify({"error": "User not found"}), 404
  db.session.delete(user)
  db.session.commit()
  return jsonify({"message": f"Successfully deleted user {token_id}"}), 200



# Update A USER
@users_bp.route("", methods=["PUT"])
@limiter.limit("1 per month")
@token_required
def update_user():
    user_id = request.logged_in_user_id
    # Query the user by id
    user = db.session.get(Users, user_id) # Query for our user to update
    if not user: # checking if I got a user with that id
       return jsonify({"message" : "User not found"}), 404
    try:
        # Validate and deserialize the updates that they are sending in the body of the request
        user_data = user_schema.load(request.json) # JSON - > Python
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    user_data["password"] = generate_password_hash(user_data["password"])
    for key, value in user_data.items():
      setattr(user,key,value) # Setting Object, Attribute, value to replace
    # Commit the changes
    db.session.commit()
    # return a response
    return user_schema.jsonify(user) , 200