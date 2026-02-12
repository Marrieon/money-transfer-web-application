from app.extensions import db
from .base import BaseModel

class Notification(BaseModel):
    __tablename__ = 'notifications'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    # Type can be used by the frontend to display different icons/actions
    # e.g., 'transfer_received', 'loan_request', 'circle_invite'
    notification_type = db.Column(db.String(50), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    
    user = db.relationship('User')

    def __repr__(self):
        return f'<Notification for User {self.user_id}>'