from app.models import User
from app.extensions import db

def upgrade_kyc_level(user_id: int, new_level: int):
    """
    Simulates upgrading a user's KYC level.
    In a real app, this would involve document verification.
    """
    user = db.session.get(User, user_id)
    if not user:
        return None

    # For now, we just update the level.
    user.kyc_level = new_level
    db.session.commit()
    return user