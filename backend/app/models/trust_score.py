from app.extensions import db
from .base import BaseModel

class TrustScoreRecord(BaseModel):
    """Stores a historical record of a user's trust score at a point in time."""
    __tablename__ = 'trust_score_records'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    # The reason for this score change, e.g., 'successful_transaction', 'loan_repaid', 'first_login'
    reason = db.Column(db.String(100), nullable=False)
    
    user = db.relationship('User', back_populates='trust_score_history')

    def __repr__(self):
        return f'<TrustScoreRecord {self.id} for User {self.user_id}: {self.score}>'