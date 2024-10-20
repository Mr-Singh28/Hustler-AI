# src/user/user_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src import db
from src.models import User
import re

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None
    
user_bp = Blueprint('user', __name__)

# Route for user registration
@user_bp.route('/register', methods=['POST'])
def register():
    try:
        # Get JSON data from the request
        data = request.get_json()
        
        # Ensure all required fields are present
        if not data or 'name' not in data or 'email' not in data or 'password' not in data:
            return jsonify({"message": "Missing required fields"}), 400

        # Validate email format
        if not is_valid_email(data['email']):
            return jsonify({"message": "Invalid email format"}), 400

        # Check if the email is already registered
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"message": "Email already registered"}), 400

        # Create a new user object
        new_user = User(name=data['name'], email=data['email'])
        new_user.set_password(data['password'])  # Hash the password

        # Add the new user to the database session
        db.session.add(new_user)
        db.session.commit()  # Save changes to the database

        # Return a success message
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        # Roll back the session in case of an error
        db.session.rollback()
        # Return an error message with the exception
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

# Route for user login
@user_bp.route('/login', methods=['POST'])
def login():
    # Get JSON data from the request
    data = request.get_json()
    
    # Find the user by email
    user = User.query.filter_by(email=data['email']).first()
    
    # Check if user exists and password is correct
    if user and user.check_password(data['password']):
        # Create an access token for the user
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    
    # If login fails, return an error message
    return jsonify({"message": "Invalid credentials"}), 401

# Route for getting and updating user profile
@user_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()  # This route requires a valid JWT token
def profile():
    # Get the current user's ID from the JWT token
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if request.method == 'GET':
        # If it's a GET request, return the user's profile information
        return jsonify({
            "name": user.name,
            "email": user.email,
            "instagram_handle": user.instagram_handle,
            "profile_picture": user.profile_picture
        }), 200
    
    elif request.method == 'PUT':
        # If it's a PUT request, update the user's profile
        data = request.get_json()
        user.name = data.get('name', user.name)  # Update name if provided, otherwise keep the old name
        user.instagram_handle = data.get('instagram_handle', user.instagram_handle)
        user.profile_picture = data.get('profile_picture', user.profile_picture)
        db.session.commit()  # Save changes to the database
        return jsonify({"message": "Profile updated successfully"}), 200