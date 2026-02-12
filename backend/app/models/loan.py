
from app.extensions import db
from .base import BaseModel

class Loan(BaseModel):
    __tablename__ = 'loans'

    lender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    amount = db.Column(db.Numeric(15, 4), nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    # Status: requested, active, paid, defaulted
    status = db.Column(db.String(20), nullable=False, default='requested')
    repayment_date = db.Column(db.Date, nullable=False)
    
    lender = db.relationship('User', foreign_keys=[lender_id])
    borrower = db.relationship('User', foreign_keys=[borrower_id])

    def __repr__(self):
        return f'<Loan {self.id} from {self.lender_id} to {self.borrower_id}>'