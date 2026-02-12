
from decimal import Decimal

def predict_spending_category(transaction_description: str) -> str:
    """
    Placeholder for a machine learning model that predicts spending category.
    In a real app, this would load a trained model (e.g., from scikit-learn or TensorFlow)
    and use it to classify the transaction.
    
    For now, we will use a simple rule-based approach.
    """
    description_lower = transaction_description.lower()
    
    if "coffee" in description_lower or "starbucks" in description_lower:
        return "Food & Drink"
    elif "uber" in description_lower or "lyft" in description_lower:
        return "Transportation"
    elif "amazon" in description_lower:
        return "Shopping"
    
    return "Uncategorized"

def predict_fraud_risk(transaction_amount: Decimal, user_trust_score: float) -> float:
    """
    Placeholder for an ML model that returns a fraud probability score (0.0 to 1.0).
    """
    # Simple rule-based risk calculation
    risk = 0.0
    if transaction_amount > 500:
        risk += 0.4
    if user_trust_score < 100:
        risk += 0.4
        
    return min(risk, 1.0)