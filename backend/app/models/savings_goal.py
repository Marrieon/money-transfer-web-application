from app.extensions import db
from .base import BaseModel

class SavingsGoal(BaseModel):
    __tablename__ = 'savings_goals'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Numeric(15, 4), nullable=False)
    current_amount = db.Column(db.Numeric(15, 4), default=0.0000, nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    
    user = db.relationship('User')

    def __repr__(self):
        return f'<SavingsGoal {self.title}>'