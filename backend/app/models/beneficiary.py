from app.extensions import db
from .base import BaseModel

class Beneficiary(BaseModel):
    __tablename__ = 'beneficiaries'
    
    # The user who owns this beneficiary record
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # The user who is the beneficiary
    beneficiary_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    nickname = db.Column(db.String(100), nullable=False)
    
    # Relationships
    owner = db.relationship('User', foreign_keys=[user_id])
    beneficiary_user = db.relationship('User', foreign_keys=[beneficiary_user_id])
    
    # Ensure a user can't add the same beneficiary twice
    __table_args__ = (db.UniqueConstraint('user_id', 'beneficiary_user_id', name='_user_beneficiary_uc'),)

    def __repr__(self):
        return f'<Beneficiary {self.nickname} for User {self.user_id}>'