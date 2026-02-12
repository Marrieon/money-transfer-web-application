from app.extensions import db
from .base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Can be null for system events
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.JSON, nullable=True)

    user = db.relationship('User')

    def __repr__(self):
        return f'<AuditLog {self.id} - {self.action}>'