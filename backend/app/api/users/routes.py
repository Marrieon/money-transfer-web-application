import json
from flask import Blueprint, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from app.models import User
from app.extensions import db
from app.utils.qr_code import generate_qr_code_base64
from app.utils.jwt_utils import get_current_user_id

users_bp = Blueprint('users_bp', __name__)

class ProfileAPI(MethodView):
    decorators = [jwt_required()]
    def get(self):
        """
        Get the current user's profile information.
        ---
        tags:
          - Users
        description: Fetches detailed profile information for the currently authenticated user.
        security:
          - bearerAuth: []
        responses:
          200:
            description: User profile data returned successfully.
          401:
            description: Unauthorized if the JWT token is missing or invalid.
          404:
            description: User not found.
        """
        user_id = get_current_user_id()
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        return jsonify({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "kyc_level": user.kyc_level,
            "trust_score": float(user.trust_score),
            "created_at": user.created_at.isoformat()
        })

class UserQRCodeAPI(MethodView):
    decorators = [jwt_required()]
    def get(self):
        """
        Generate a QR code for receiving payments.
        ---
        tags:
          - Users
        description: Creates a base64-encoded QR code image containing the user's phone number, which can be scanned by others to initiate a payment.
        security:
          - bearerAuth: []
        responses:
          200:
            description: A JSON object containing the base64 data URI of the QR code.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    qr_code:
                      type: string
                      example: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
          401:
            description: Unauthorized if the JWT token is missing or invalid.
        """
        user_id = get_current_user_id()
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        qr_data = json.dumps({"type": "user_payment", "phone": user.phone})
        qr_image_b64 = generate_qr_code_base64(qr_data)

        return jsonify({"qr_code": qr_image_b64})

# Registering the URL rules
users_bp.add_url_rule('/profile', view_func=ProfileAPI.as_view('profile_api'))
users_bp.add_url_rule('/qr-code', view_func=UserQRCodeAPI.as_view('user_qr_code_api'))
