from flask import Blueprint, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from app.services.analytics_service import get_spending_summary_by_category
from app.utils.jwt_utils import get_current_user_id

analytics_bp = Blueprint('analytics_bp', __name__)

class SpendingSummaryAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        """
        Get a summary of the user's spending by category.
        ---
        tags:
          - Analytics
        description: >
          Retrieves a summary of the authenticated user's total spending,
          grouped by transaction category. This is a core component of the
          "AI-Powered Financial Insights" value proposition. Only transactions
          of type 'transfer' are counted as spending.
        security:
          - bearerAuth: []
        responses:
          200:
            description: A summary object of spending by category.
            content:
              application/json:
                schema:
                  type: object
                  additionalProperties:
                    type: number
                    format: float
                  example:
                    "Uncategorized": 150.75,
                    "Shopping": 85.50,
                    "Food & Drink": 45.20
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        
        # Call the dedicated service function to perform the business logic.
        summary = get_spending_summary_by_category(user_id)
        
        return jsonify(summary)

# Register the URL rule for the SpendingSummaryAPI class.
analytics_bp.add_url_rule(
    '/spending-summary', 
    view_func=SpendingSummaryAPI.as_view('spending_summary_api')
)
