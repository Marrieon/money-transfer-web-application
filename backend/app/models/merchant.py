from app.extensions import db
from .base import BaseModel
import uuid

def generate_api_key():
    """Generates a simple unique API key."""
    return str(uuid.uuid4())

class Merchant(BaseModel):
    """Represents a merchant account for a user."""
    __tablename__ = 'merchants'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    business_name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(100), unique=True, nullable=False, default=generate_api_key)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    user = db.relationship('User')