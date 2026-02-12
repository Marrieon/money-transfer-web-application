from decimal import Decimal
from app.models import Transaction, User

def check_for_fraud(sender: User, transaction_amount: Decimal, is_new_beneficiary: bool) -> bool:
    """
    Checks a transaction against a set of fraud rules.
    Returns True if the transaction is suspicious, False otherwise.
    """
    # Rule 1: High-value transaction from a user with a low trust score.
    if transaction_amount > 500 and sender.trust_score < 100:
        return True # Flag as suspicious

    # Rule 2: Multiple high-value transactions in a short period.
    # (This requires more complex state/cache, will be implemented later)

    # Rule 3: Transaction amount is unusually high compared to user's average.
    # (Requires analytics service, will be implemented later)

    # Rule 4: High-value transfer to a brand new beneficiary.
    if transaction_amount > 200 and is_new_beneficiary:
        return True # Flag as suspicious

    # If no rules are triggered, the transaction is not considered fraudulent.
    return False