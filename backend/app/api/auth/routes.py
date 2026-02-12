from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import create_access_token
from app.models import User, Wallet
from app.extensions import db
from app.utils.exceptions import InvalidUsage
from app.services.audit_service import log_action
from app.services.auth_service import register_user, authenticate_user

auth_bp = Blueprint('auth_bp', __name__)

class RegisterAPI(MethodView):
    def post(self):
        """
        Register a new user account.
        ---
        tags:
          - Authentication
        description: Creates a new user and an associated wallet with a starting balance.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  email:
                    type: string
                    example: user@example.com
                  phone:
                    type: string
                    example: "1234567890"
                  password:
                    type: string
                    format: password
                    example: "password123"
                  first_name:
                    type: string
                    example: "John"
                  last_name:
                    type: string
                    example: "Doe"
        responses:
          201:
            description: User created successfully.
          400:
            description: Invalid input, missing fields, or user with that email/phone already exists.
        """
        data = request.get_json()
        try:
            user = register_user(
                email=data.get('email'),
                phone=data.get('phone'),
                password=data.get('password'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name')
            )
            log_action("user_registered", user_id=user.id, details={'email': user.email})
            db.session.commit()
        except InvalidUsage as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            raise InvalidUsage(f"Could not create user: {str(e)}")

        return jsonify(message="User created successfully"), 201

class LoginAPI(MethodView):
    def post(self):
        """
        Authenticate a user and return a JWT token.
        ---
        tags:
          - Authentication
        description: Logs in a user by verifying their email and password.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  email:
                    type: string
                    example: user@example.com
                  password:
                    type: string
                    format: password
                    example: "password123"
        responses:
          200:
            description: Login successful.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    access_token:
                      type: string
          400:
            description: Invalid email, password, or missing fields.
        """
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise InvalidUsage("Email and password are required")
        
        access_token = authenticate_user(email, password)

        if access_token:
            user = User.query.filter_by(email=email).first()
            log_action("user_login_success", user_id=user.id)
            db.session.commit()
            return jsonify(access_token=access_token)
        else:
            log_action("user_login_failed", details={'email': email})
            db.session.commit()
            raise InvalidUsage("Invalid email or password")

# Registering the URL rules for the API views
auth_bp.add_url_rule('/register', view_func=RegisterAPI.as_view('register_api'))
auth_bp.add_url_rule('/login', view_func=LoginAPI.as_view('login_api'))