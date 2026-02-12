from app.models import User, Wallet
from app.extensions import db
from flask_jwt_extended import create_access_token
from app.utils.exceptions import InvalidUsage

def register_user(email, phone, password, first_name, last_name):
    """
    Handles the business logic for user registration.
    Checks for duplicates, creates user and wallet, and hashes password.
    """
    if User.query.filter((User.email == email) | (User.phone == phone)).first():
        raise InvalidUsage("User with this email or phone already exists")
    
    user = User(email=email, phone=phone, first_name=first_name, last_name=last_name)
    user.set_password(password)
    
    # A wallet is created and associated with the user automatically
    # when the user is committed, due to the cascade relationship.
    # However, we must instantiate it to set the initial balance.
    wallet = Wallet(user=user, balance=100.00)
    
    db.session.add(user)
    db.session.add(wallet)
    
    return user

def authenticate_user(email, password):
    """
    Handles the business logic for user authentication.
    Returns a JWT token on success, None on failure.
    """
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return create_access_token(identity=str(user.id))
    return None
