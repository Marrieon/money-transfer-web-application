from datetime import date, timedelta
# MODIFIED: Import the raw function, not the Celery proxy
from app.tasks.social_tasks import check_overdue_loans_task
from app.models import Loan, User, Notification
from app.extensions import db

def test_check_overdue_loans(client, init_database):
    """Test the scheduled task correctly identifies and updates overdue loans."""
    # Setup: Get users from the fixture
    lender = User.query.filter_by(email='user1@test.com').first()
    borrower = User.query.filter_by(email='user2@test.com').first()
    
    # Create an 'active' loan that is now overdue
    overdue_loan = Loan(
        lender_id=lender.id,
        borrower_id=borrower.id,
        amount=100,
        interest_rate=5.0,
        status='active',
        repayment_date=date.today() - timedelta(days=1)
    )
    db.session.add(overdue_loan)
    
    # This time we will use commit() because the task will run
    # as a plain function within the same session context that the test continues in.
    db.session.commit()
    
    # MODIFIED (The Fix): Call the task as a regular Python function.
    # This completely avoids the Celery worker/session mechanism and prevents deadlocks.
    result_message = check_overdue_loans_task()
    
    # Assertions
    # 1. Check the task's return message
    assert "Updated 1 loans" in result_message
    
    # 2. Check the loan's status in the database
    updated_loan = db.session.get(Loan, overdue_loan.id)
    assert updated_loan.status == 'defaulted'
    
    # 3. Check that the borrower received a notification
    borrower_notification = Notification.query.filter_by(user_id=borrower.id, notification_type='loan_defaulted').first()
    assert borrower_notification is not None
    
    # 4. Check that the borrower's trust score was penalized
    # The 'borrower' object is now stale, we must get the fresh version from the DB.
    updated_borrower = db.session.get(User, borrower.id)
    assert updated_borrower.trust_score < 50.0