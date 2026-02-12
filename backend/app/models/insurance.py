from app.extensions import db
from .base import BaseModel

class InsuranceProduct(BaseModel):
    """Represents an available insurance product, e.g., 'Device Protection'."""
    __tablename__ = 'insurance_products'

    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    coverage_amount = db.Column(db.Numeric(15, 4), nullable=False)
    premium_amount = db.Column(db.Numeric(15, 4), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

class UserInsurancePolicy(BaseModel):
    """Represents a user's purchased insurance policy."""
    __tablename__ = 'user_insurance_policies'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('insurance_products.id'), nullable=False)
    
    # Status: active, expired, claimed
    status = db.Column(db.String(20), default='active', nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    end_date = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User')
    product = db.relationship('InsuranceProduct')