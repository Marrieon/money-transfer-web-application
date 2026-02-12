from flask import Blueprint, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Notification
from app.utils.jwt_utils import get_current_user_id

notifications_bp = Blueprint('notifications_bp', __name__)

class NotificationAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        """
        Get all notifications for the current user.
        ---
        tags:
          - Notifications
        description: Retrieves a list of all notifications for the authenticated user, sorted by most recent first.
        security:
          - bearerAuth: []
        responses:
          200:
            description: A list of the user's notifications.
            content:
              application/json:
                schema:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      message:
                        type: string
                        example: "You have received a payment of $50.00."
                      type:
                        type: string
                        example: "transfer_received"
                      is_read:
                        type: boolean
                      created_at:
                        type: string
                        format: date-time
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        # Order by most recent first
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
        
        return jsonify([{
            "id": n.id,
            "message": n.message,
            "type": n.notification_type,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        } for n in notifications])

    def post(self):
        """
        Mark all notifications as read.
        ---
        tags:
          - Notifications
        description: Marks all unread notifications for the authenticated user as read. This is a bulk action.
        security:
          - bearerAuth: []
        responses:
          200:
            description: Confirmation that notifications were marked as read.
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return jsonify({"message": "All notifications marked as read."})

notifications_bp.add_url_rule('/', view_func=NotificationAPI.as_view('notification_api'), methods=['GET', 'POST'])
# Allow clients that omit the trailing slash to avoid preflight redirects.
notifications_bp.add_url_rule('', view_func=NotificationAPI.as_view('notification_api_no_slash'), methods=['GET', 'POST'])
