from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from decimal import Decimal
from app.extensions import db
from app.models import User, MoneyCircle
from app.utils.exceptions import InvalidUsage, NotFound
from app.utils.jwt_utils import get_current_user_id

circles_bp = Blueprint('circles_bp', __name__)

class MoneyCircleAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        """
        Get all money circles a user is a member of.
        ---
        tags:
          - Money Circles
        description: Retrieves a list of all money circles (or 'chamas') that the authenticated user is currently a member of.
        security:
          - bearerAuth: []
        responses:
          200:
            description: A list of the user's money circles.
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        user = db.session.get(User, user_id)
        if not user:
            raise NotFound("User not found.")
        
        circles = user.money_circles
        
        return jsonify([{
            "id": c.id,
            "name": c.name,
            "contribution_amount": float(c.contribution_amount),
            "frequency_days": c.frequency,
            "member_count": len(c.members)
        } for c in circles])

    def post(self):
        """
        Create a new money circle.
        ---
        tags:
          - Money Circles
        description: Creates a new money circle (or 'chama') where the authenticated user is automatically set as the creator and first member.
        security:
          - bearerAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  name:
                    type: string
                    example: "Neighborhood Savings Group"
                  contribution_amount:
                    type: string
                    example: "50.00"
                  frequency:
                    type: integer
                    description: "Contribution frequency in days (e.g., 7 for weekly, 30 for monthly). Defaults to 30."
                    example: 30
                required:
                  - name
                  - contribution_amount
        responses:
          201:
            description: Money circle created successfully.
          400:
            description: Bad request due to missing fields or invalid data.
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        data = request.get_json()
        name = data.get('name')
        contribution_str = data.get('contribution_amount')
        frequency = data.get('frequency', 30)

        if not name or not contribution_str:
            raise InvalidUsage("Name and contribution_amount are required.")
            
        try:
            contribution = Decimal(contribution_str)
        except:
            raise InvalidUsage("Invalid contribution amount format.")

        user = db.session.get(User, user_id)
        if not user:
            raise NotFound("User not found.")

        circle = MoneyCircle(
            name=name,
            contribution_amount=contribution,
            frequency=frequency,
            creator=user
        )
        # The creator is automatically a member
        circle.members.append(user)
        
        db.session.add(circle)
        db.session.commit()
        
        return jsonify({"message": "Money circle created", "id": circle.id}), 201

circles_bp.add_url_rule('/', view_func=MoneyCircleAPI.as_view('money_circle_api'), methods=['GET', 'POST'])
