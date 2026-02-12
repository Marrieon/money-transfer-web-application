import bcrypt
from app.extensions import db
from .base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    kyc_level = db.Column(db.Integer, default=0)
    trust_score = db.Column(db.Float, default=50.0)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # --- RELATIONSHIPS ---
    # This section defines how the User model links to other models.
    # The error was caused by one of these lines being missing.

    # (Phase 1) The one-to-one relationship to the User's Wallet.
    wallet = db.relationship('Wallet', back_populates='user', uselist=False, cascade="all, delete-orphan")
    
    # (Phase 1) The one-to-many relationship for transactions this user has sent.
    transactions_sent = db.relationship('Transaction', foreign_keys='Transaction.sender_id', back_populates='sender', lazy='dynamic')
    
    # (Phase 1) The one-to-many relationship for transactions this user has received.
    transactions_received = db.relationship('Transaction', foreign_keys='Transaction.receiver_id', back_populates='receiver', lazy='dynamic')
    
    # (Phase 4) The one-to-many relationship for this user's trust score history.
    trust_score_history = db.relationship('TrustScoreRecord', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")


    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.email}>'