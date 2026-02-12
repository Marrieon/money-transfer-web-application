from decimal import Decimal
from app.services.fraud_detection import check_for_fraud
from app.models import User

def test_fraud_check_high_value_low_trust(client, init_database):
    """Test Rule 1: High value transaction from a low-trust user is fraud."""
    low_trust_user = User.query.filter_by(email='user1@test.com').first()
    # Manually set a low trust score for this specific test case
    low_trust_user.trust_score = 20.0

    is_fraud = check_for_fraud(
        sender=low_trust_user, 
        transaction_amount=Decimal("600.00"), 
        is_new_beneficiary=False
    )
    
    assert is_fraud is True, "Should be flagged as fraud due to low trust and high value"

def test_fraud_check_normal_value_low_trust(client, init_database):
    """Test that a normal transaction from a low-trust user is NOT fraud."""
    low_trust_user = User.query.filter_by(email='user1@test.com').first()
    low_trust_user.trust_score = 20.0

    is_fraud = check_for_fraud(
        sender=low_trust_user, 
        transaction_amount=Decimal("50.00"), 
        is_new_beneficiary=False
    )
    
    assert is_fraud is False, "Should not be flagged as fraud for normal value"

def test_fraud_check_high_value_new_beneficiary(client, init_database):
    """Test Rule 4: High value transaction to a new beneficiary is fraud."""
    user = User.query.filter_by(email='user1@test.com').first()
    # User has a normal trust score
    user.trust_score = 200.0

    is_fraud = check_for_fraud(
        sender=user, 
        transaction_amount=Decimal("250.00"), 
        is_new_beneficiary=True # The key condition for this rule
    )
    
    assert is_fraud is True, "Should be flagged as fraud due to high value and new beneficiary"