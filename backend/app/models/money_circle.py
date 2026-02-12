from app.extensions import db
from .base import BaseModel

# Association table for the many-to-many relationship between Users and MoneyCircles
money_circle_members = db.Table('money_circle_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('circle_id', db.Integer, db.ForeignKey('money_circles.id'), primary_key=True)
)

class MoneyCircle(BaseModel):
    __tablename__ = 'money_circles'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    contribution_amount = db.Column(db.Numeric(15, 4), nullable=False)
    # Frequency in days (e.g., 7 for weekly, 30 for monthly)
    frequency = db.Column(db.Integer, nullable=False, default=30)
    
    # The user who created and manages the circle
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship('User')
    
    # Many-to-many relationship for members
    members = db.relationship('User', secondary=money_circle_members, lazy='subquery',
                              backref=db.backref('money_circles', lazy=True))

    def __repr__(self):
        return f'<MoneyCircle {self.name}>'
