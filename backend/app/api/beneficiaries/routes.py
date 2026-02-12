from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import User, Beneficiary
from app.utils.exceptions import InvalidUsage, NotFound
from app.utils.jwt_utils import get_current_user_id

beneficiaries_bp = Blueprint('beneficiaries_bp', __name__)

class BeneficiaryAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        """
        Get all of a user's saved beneficiaries.
        ---
        tags:
          - Beneficiaries
        description: Retrieves a list of saved contacts (beneficiaries) for the authenticated user, making it easier to send them money in the future.
        security:
          - bearerAuth: []
        responses:
          200:
            description: A list of the user's beneficiaries.
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        beneficiaries = Beneficiary.query.filter_by(user_id=user_id).all()
        
        return jsonify([{
            "id": b.id,
            "nickname": b.nickname,
            "beneficiary_user": {
                "id": b.beneficiary_user.id,
                "first_name": b.beneficiary_user.first_name,
                "last_name": b.beneficiary_user.last_name,
                "phone": b.beneficiary_user.phone
            }
        } for b in beneficiaries])

    def post(self):
        """
        Add a new beneficiary.
        ---
        tags:
          - Beneficiaries
        description: Adds another registered user to the authenticated user's list of saved beneficiaries.
        security:
          - bearerAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  phone:
                    type: string
                    description: "The phone number of the user to add as a beneficiary."
                    example: "2222222222"
                  nickname:
                    type: string
                    description: "A friendly name to remember this beneficiary by."
                    example: "Work Friend"
                required:
                  - phone
                  - nickname
        responses:
          201:
            description: Beneficiary added successfully.
          400:
            description: Bad request, user may already be a beneficiary or is trying to add themselves.
          401:
            description: Unauthorized.
          404:
            description: User with the specified phone number not found.
        """
        user_id = get_current_user_id()
        data = request.get_json()
        beneficiary_phone = data.get('phone')
        nickname = data.get('nickname')

        if not beneficiary_phone or not nickname:
            raise InvalidUsage("Phone and nickname are required.")
        
        beneficiary_user = User.query.filter_by(phone=beneficiary_phone).first()
        if not beneficiary_user:
            raise NotFound("User with this phone number not found.")
        
        if user_id == beneficiary_user.id:
            raise InvalidUsage("You cannot add yourself as a beneficiary.")

        existing = Beneficiary.query.filter_by(user_id=user_id, beneficiary_user_id=beneficiary_user.id).first()
        if existing:
            raise InvalidUsage("This user is already a beneficiary.")
            
        beneficiary = Beneficiary(
            user_id=user_id,
            beneficiary_user_id=beneficiary_user.id,
            nickname=nickname
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        return jsonify({"message": "Beneficiary added successfully", "id": beneficiary.id}), 201

beneficiaries_bp.add_url_rule('/', view_func=BeneficiaryAPI.as_view('beneficiary_api'), methods=['GET', 'POST'])
