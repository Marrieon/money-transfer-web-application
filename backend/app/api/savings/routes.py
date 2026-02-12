from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from decimal import Decimal
from datetime import date
from app.extensions import db
from app.models import SavingsGoal
from app.services.wallet_service import transfer_to_savings_goal
from app.utils.exceptions import InvalidUsage, NotFound
from app.utils.jwt_utils import get_current_user_id

savings_bp = Blueprint('savings_bp', __name__)

class SavingsGoalAPI(MethodView):
    decorators = [jwt_required()]

    def get(self, goal_id=None):
        """
        Get all savings goals or a specific one.
        ---
        tags:
          - Savings
        description: If a goal_id is provided, it retrieves a single savings goal. Otherwise, it returns a list of all savings goals for the authenticated user.
        security:
          - bearerAuth: []
        parameters:
          - in: path
            name: goal_id
            required: false
            schema:
              type: integer
            description: The ID of the specific savings goal to retrieve.
        responses:
          200:
            description: A single savings goal object or a list of savings goals.
          401:
            description: Unauthorized.
          404:
            description: Savings goal not found.
        """
        user_id = get_current_user_id()
        if goal_id:
            goal = db.session.get(SavingsGoal, goal_id)
            if not goal or goal.user_id != user_id:
                raise NotFound("Goal not found.")
            return jsonify({
                "id": goal.id,
                "title": goal.title,
                "target_amount": float(goal.target_amount),
                "current_amount": float(goal.current_amount),
                "deadline": goal.deadline.isoformat() if goal.deadline else None
            })
        
        goals = SavingsGoal.query.filter_by(user_id=user_id).all()
        return jsonify([{
            "id": g.id, "title": g.title, "target_amount": float(g.target_amount), 
            "current_amount": float(g.current_amount)
        } for g in goals])

    def post(self):
        """
        Create a new savings goal.
        ---
        tags:
          - Savings
        description: Creates a new savings goal for the authenticated user.
        security:
          - bearerAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  title:
                    type: string
                    example: "New Car Fund"
                  target_amount:
                    type: string
                    example: "20000.00"
                  deadline:
                    type: string
                    format: date
                    example: "2026-12-31"
                required:
                  - title
                  - target_amount
        responses:
          201:
            description: Savings goal created successfully.
          400:
            description: Bad request due to missing fields or invalid data.
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        data = request.get_json()
        title = data.get('title')
        target_amount_str = data.get('target_amount')
        deadline_str = data.get('deadline')

        if not title or not target_amount_str:
            raise InvalidUsage("Title and target_amount are required.")

        try:
            target_amount = Decimal(target_amount_str)
            deadline = date.fromisoformat(deadline_str) if deadline_str else None
        except (ValueError, TypeError):
            raise InvalidUsage("Invalid amount or date format. Use YYYY-MM-DD for deadline.")

        goal = SavingsGoal(
            user_id=user_id,
            title=title,
            target_amount=target_amount,
            deadline=deadline
        )
        db.session.add(goal)
        db.session.commit()
        
        return jsonify({"message": "Savings goal created", "id": goal.id}), 201

class SavingsDepositAPI(MethodView):
    decorators = [jwt_required()]

    def post(self, goal_id):
        """
        Deposit funds into a savings goal.
        ---
        tags:
          - Savings
        description: Transfers a specified amount from the user's main wallet to one of their savings goals.
        security:
          - bearerAuth: []
        parameters:
          - in: path
            name: goal_id
            required: true
            schema:
              type: integer
            description: The ID of the savings goal to deposit into.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  amount:
                    type: string
                    example: "100.00"
                required:
                  - amount
        responses:
          200:
            description: Deposit was successful.
          400:
            description: Bad request due to invalid amount or insufficient funds.
          401:
            description: Unauthorized.
          404:
            description: Savings goal not found.
        """
        user_id = get_current_user_id()
        data = request.get_json()
        
        try:
            amount = Decimal(data.get('amount'))
        except (ValueError, TypeError, InvalidUsage):
             raise InvalidUsage("Invalid amount format.")

        updated_goal = transfer_to_savings_goal(user_id, goal_id, amount)
        
        return jsonify({
            "message": "Deposit successful",
            "goal_id": updated_goal.id,
            "new_balance": float(updated_goal.current_amount)
        })

savings_bp.add_url_rule('/goals', view_func=SavingsGoalAPI.as_view('savings_goals_api'), methods=['GET', 'POST'])
savings_bp.add_url_rule('/goals/<int:goal_id>', view_func=SavingsGoalAPI.as_view('savings_goal_detail_api'), methods=['GET'])
savings_bp.add_url_rule('/goals/<int:goal_id>/deposit', view_func=SavingsDepositAPI.as_view('savings_deposit_api'), methods=['POST'])
