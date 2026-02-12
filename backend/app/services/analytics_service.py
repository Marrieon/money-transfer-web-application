from sqlalchemy import func
from app.extensions import db
from app.models import User, Transaction

def get_admin_dashboard_stats():
    """Calculates key statistics for the admin dashboard."""
    total_users = db.session.query(func.count(User.id)).scalar()
    total_transactions = db.session.query(func.count(Transaction.id)).scalar()
    total_volume = db.session.query(func.sum(Transaction.amount)).scalar() or 0
    total_revenue = db.session.query(func.sum(Transaction.fee)).scalar() or 0

    return {
        "total_users": total_users,
        "total_transactions": total_transactions,
        "total_volume": float(total_volume),
        "total_revenue": float(total_revenue)
    }

def get_spending_summary_by_category(user_id: int):
    """Calculates a user's spending summary grouped by category."""
    summary = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount)
    ).filter(
        Transaction.sender_id == user_id,
        Transaction.type == 'transfer' # Only count transfers as spending
    ).group_by(Transaction.category).all()

    return {category: float(total) for category, total in summary}