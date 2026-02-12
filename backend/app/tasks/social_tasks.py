from datetime import date
from . import celery
from app.extensions import db
from app.models import Loan
from app.services.notification_service import create_notification
from app.services.trust_service import update_trust_score

# MODIFIED: The core logic is now in a plain function
def check_overdue_loans_task():
    """
    Core logic for checking and handling overdue loans.
    This can be called directly for testing.
    """
    today = date.today()
    
    overdue_loans = Loan.query.filter(
        Loan.status == 'active',
        Loan.repayment_date < today
    ).all()
    
    if not overdue_loans:
        return "No overdue loans found."

    updated_count = 0
    for loan in overdue_loans:
        loan.status = 'defaulted'
        
        lender_message = f"Your loan of {loan.amount} to {loan.borrower.first_name} is overdue and has been marked as defaulted."
        borrower_message = f"Your loan of {loan.amount} from {loan.lender.first_name} is overdue and has been marked as defaulted."
        create_notification(loan.lender_id, lender_message, "loan_defaulted", True)
        create_notification(loan.borrower_id, borrower_message, "loan_defaulted", True)
        
        update_trust_score(loan.borrower_id, "loan_defaulted", -50)
        update_trust_score(loan.lender_id, "loan_lent_defaulted", -5)
        
        updated_count += 1
        
    db.session.commit()
    
    return f"Updated {updated_count} loans to 'defaulted'."


# The Celery task is now just a thin wrapper around our testable function.
@celery.task(name='app.tasks.social_tasks.check_overdue_loans')
def check_overdue_loans():
    """Celery wrapper for the overdue loans task."""
    return check_overdue_loans_task()