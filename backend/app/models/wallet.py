from app.extensions import db
from .base import BaseModel

class Wallet(BaseModel):
    __tablename__ = 'wallets'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    currency = db.Column(db.String(10), default='USD', nullable=False)
    
    # MODIFIED: Increased precision from 2 to 4 decimal places for financial accuracy.
    # The default value is also updated to match the new precision.
    balance = db.Column(db.Numeric(15, 4), default=0.0000, nullable=False)
    
    status = db.Column(db.String(20), default='active', nullable=False)

    user = db.relationship('User', back_populates='wallet')

    def __repr__(self):
        return f'<Wallet {self.id} for User {self.user_id}>'