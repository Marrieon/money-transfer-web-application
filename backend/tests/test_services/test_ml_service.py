from decimal import Decimal
from app.services import ml_service

def test_predict_spending_category():
    """Test the rule-based category prediction."""
    
    assert ml_service.predict_spending_category("UBER TRIP") == "Transportation"
    assert ml_service.predict_spending_category("Starbucks Coffee") == "Food & Drink"
    assert ml_service.predict_spending_category("amazon.com purchase") == "Shopping"
    assert ml_service.predict_spending_category("Local grocery store") == "Uncategorized"

def test_predict_fraud_risk():
    """Test the rule-based fraud risk prediction."""
    
    # Low risk
    low_risk = ml_service.predict_fraud_risk(Decimal("50.00"), 300.0)
    assert low_risk == 0.0
    
    # Medium risk (high amount)
    medium_risk = ml_service.predict_fraud_risk(Decimal("600.00"), 300.0)
    assert medium_risk == 0.4
    
    # High risk (high amount and low trust)
    high_risk = ml_service.predict_fraud_risk(Decimal("600.00"), 50.0)
    assert high_risk == 0.8