from app.extensions import db
from app.models import User, TrustScoreRecord
from sqlalchemy import func

def update_trust_score(user_id: int, reason: str, point_change: float):
    """
    Updates a user's trust score and creates a historical record.
    Positive points increase trust, negative points decrease it.
    """
    user = db.session.get(User, user_id)
    if not user:
        return

    # Calculate new score, ensuring it stays between 0 and 999 (or your chosen max)
    new_score = user.trust_score + point_change
    user.trust_score = max(0, min(new_score, 999))

    # Create a record of this change
    record = TrustScoreRecord(
        user_id=user_id,
        score=user.trust_score,
        reason=reason
    )
    db.session.add(record)
    # The commit will be handled by the calling function's request cycle.
    
    return user.trust_score

def recalculate_full_trust_score(user_id: int):
    """
    A more intensive function that recalculates the score from scratch based on all historical activities.
    This could be run periodically by a background task.
    """
    user = db.session.get(User, user_id)
    if not user:
        return 0

    # Start with a baseline score
    score = 50.0
    
    # Add points for successful transactions
    successful_transfers = user.transactions_sent.filter_by(status='completed').count()
    score += successful_transfers * 1.5 # 1.5 points per transfer

    # Add points for savings
    total_saved = user.savings_goals.with_entities(func.sum(user.savings_goals.current_amount)).scalar()
    if total_saved and total_saved > 0:
        score += float(total_saved) / 10 # 1 point for every $10 saved

    # Add points for repaying loans (future implementation)
    # repaid_loans = user.loans_as_borrower.filter_by(status='paid').count()
    # score += repaid_loans * 25
    
    # Ensure score has a floor and ceiling
    final_score = max(0, min(score, 999))
    user.trust_score = final_score

    record = TrustScoreRecord(
        user_id=user_id,
        score=final_score,
        reason="periodic_recalculation"
    )
    db.session.add(record)
    db.session.commit()
    return final_score