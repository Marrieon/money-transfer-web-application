from flask import Blueprint, jsonify
from flask.views import MethodView
from app.models import User, Transaction
from app.utils.decorators import admin_required
from app.services.analytics_service import get_admin_dashboard_stats

admin_bp = Blueprint('admin_bp', __name__)

class UserListAPI(MethodView):
    decorators = [admin_required()]

    def get(self):
        """
        (Admin) Get a list of all users.
        ---
        tags:
          - Admin
        description: Retrieves a complete list of all users registered in the system. Requires admin privileges.
        security:
          - bearerAuth: []
        responses:
          200:
            description: A list of user objects.
          401:
            description: Unauthorized (only admins can access this).
        """
        users = User.query.all()
        return jsonify([{
            'id': u.id,
            'email': u.email,
            'phone': u.phone,
            'is_admin': u.is_admin,
            'created_at': u.created_at.isoformat()
        } for u in users])

class TransactionListAPI(MethodView):
    decorators = [admin_required()]
    
    def get(self):
        """
        (Admin) Get a list of all transactions.
        ---
        tags:
          - Admin
        description: Retrieves a complete list of all transactions that have occurred in the system, sorted by most recent first. Requires admin privileges.
        security:
          - bearerAuth: []
        responses:
          200:
            description: A list of transaction objects.
          401:
            description: Unauthorized (only admins can access this).
        """
        transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
        return jsonify([{
            'id': t.id,
            'sender_id': t.sender_id,
            'receiver_id': t.receiver_id,
            'amount': float(t.amount),
            'fee': float(t.fee),
            'status': t.status,
            'date': t.created_at.isoformat()
        } for t in transactions])

class AdminStatsAPI(MethodView):
    decorators = [admin_required()]

    def get(self):
        """
        (Admin) Get key dashboard statistics.
        ---
        tags:
          - Admin
        description: Retrieves key metrics for the admin dashboard, such as total users, total transactions, and total revenue. Requires admin privileges.
        security:
          - bearerAuth: []
        responses:
          200:
            description: A JSON object with dashboard statistics.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    total_users:
                      type: integer
                    total_transactions:
                      type: integer
                    total_volume:
                      type: number
                      format: float
                    total_revenue:
                      type: number
                      format: float
          401:
            description: Unauthorized (only admins can access this).
        """
        stats = get_admin_dashboard_stats()
        return jsonify(stats)

# Register URL rules
admin_bp.add_url_rule('/users', view_func=UserListAPI.as_view('admin_user_list_api'))
admin_bp.add_url_rule('/transactions', view_func=TransactionListAPI.as_view('admin_transaction_list_api'))
admin_bp.add_url_rule('/stats', view_func=AdminStatsAPI.as_view('admin_stats_api'))