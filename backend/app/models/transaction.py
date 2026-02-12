from app.extensions import db
from .base import BaseModel

class Transaction(BaseModel):
    __tablename__ = 'transactions'

    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    amount = db.Column(db.Numeric(15, 4), nullable=False)
    currency = db.Column(db.String(10), default='USD', nullable=False)
    fee = db.Column(db.Numeric(10, 4), default=0.0000, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    type = db.Column(db.String(20), nullable=False)
    
    # NEW: Add a category for budgeting
    category = db.Column(db.String(50), nullable=True, default='Uncategorized')

    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='transactions_sent')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='transactions_received')

    def __repr__(self):
        return f'<Transaction {self.id} from {self.sender_id} to {self.receiver_id}>'