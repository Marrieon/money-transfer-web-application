from app.extensions import db
from app.models import Notification, User
# NEW: Import the SMS service
from app.api.external.sms_service import send_sms

def create_notification(user_id: int, message: str, notification_type: str, send_sms_notification: bool = False):
    """
    Creates an in-app notification and optionally sends an SMS.
    
    Args:
        user_id (int): The ID of the user to notify.
        message (str): The notification message.
        notification_type (str): The type of notification.
        send_sms_notification (bool): If True, an SMS will also be sent.
    """
    user = db.session.get(User, user_id)
    if not user:
        return

    # 1. Create the in-app notification (existing logic)
    notification = Notification(
        user_id=user_id,
        message=message,
        notification_type=notification_type
    )
    db.session.add(notification)

    # 2. Send SMS if requested (NEW logic)
    if send_sms_notification:
        # We can send a slightly shorter message for SMS
        sms_message = f"MoneyTransferApp: {message}"
        send_sms(to_phone=user.phone, message=sms_message)
    
    # The session will be committed by the calling route's logic.