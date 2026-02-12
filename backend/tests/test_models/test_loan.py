from datetime import date, timedelta
from decimal import Decimal
from app.models import Loan, User
from app.extensions import db

def test_loan_creation(client, init_database):
    """
    Test that a Loan record can be successfully created with its default status.
    """
    # Get the lender (user1) and borrower (user2) from the test fixture
    lender_user = User.query.filter_by(email='user1@test.com').first()
    borrower_user = User.query.filter_by(email='user2@test.com').first()
    
    # 1. Create a new Loan instance
    loan = Loan(
        lender_id=lender_user.id,
        borrower_id=borrower_user.id,
        amount=Decimal("500.00"),
        interest_rate=5.5,
        repayment_date=date.today() + timedelta(days=90)
    )
    
    # 2. Add and commit to the database
    db.session.add(loan)
    db.session.commit()
    
    # 3. Verify the record was created and has an ID
    assert loan.id is not None
    
    # 4. Fetch the record and check its attributes
    retrieved_loan = db.session.get(Loan, loan.id)
    assert retrieved_loan is not None
    assert retrieved_loan.lender_id == lender_user.id
    assert retrieved_loan.borrower_id == borrower_user.id
    assert retrieved_loan.amount == Decimal("500.00")
    # Check the default value for 'status'
    assert retrieved_loan.status == 'requested'

def test_loan_relationships(client, init_database):
    """
    Test that the 'lender' and 'borrower' relationships are correctly linked.
    """
    lender_user = User.query.filter_by(email='user1@test.com').first()
    borrower_user = User.query.filter_by(email='user2@test.com').first()
    
    loan = Loan(
        lender_id=lender_user.id,
        borrower_id=borrower_user.id,
        amount=Decimal("150.00"),
        interest_rate=10.0,
        repayment_date=date.today() + timedelta(days=30)
    )
    db.session.add(loan)
    db.session.commit()
    
    # Fetch the loan and test the relationships
    retrieved_loan = db.session.get(Loan, loan.id)
    
    # Test the 'lender' relationship
    assert retrieved_loan.lender is not None
    assert retrieved_loan.lender.email == lender_user.email
    
    # Test the 'borrower' relationship
    assert retrieved_loan.borrower is not None
    assert retrieved_loan.borrower.email == borrower_user.email