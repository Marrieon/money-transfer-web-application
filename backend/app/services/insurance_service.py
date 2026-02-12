from datetime import datetime, timedelta
from decimal import Decimal
from app.extensions import db
from app.models import User, InsuranceProduct, UserInsurancePolicy, Transaction, Wallet
from app.utils.exceptions import InvalidUsage, NotFound

def purchase_insurance(user_id: int, product_id: int):
    """Handles the logic for a user purchasing an insurance policy."""
    user = db.session.get(User, user_id)
    product = db.session.get(InsuranceProduct, product_id)

    if not user or not user.wallet:
        raise NotFound("User or wallet not found.")
    if not product or not product.is_active:
        raise NotFound("Insurance product not found or is not active.")

    wallet = user.wallet
    premium = product.premium_amount

    if wallet.balance < premium:
        raise InvalidUsage("Insufficient funds to purchase insurance.")

    try:
        # 1. Debit the user's wallet for the premium
        wallet.balance -= premium

        # 2. Create a transaction record for this purchase
        transaction = Transaction(
            sender_id=user_id,
            receiver_id=user_id, # Internal transaction
            amount=premium,
            fee=0,
            status='completed',
            type='insurance_purchase',
            category='Financial Services'
        )
        db.session.add(transaction)

        # 3. Create the user's insurance policy
        # For simplicity, we'll make all policies last for 1 year (365 days)
        policy = UserInsurancePolicy(
            user_id=user_id,
            product_id=product_id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=365)
        )
        db.session.add(policy)

        db.session.commit()
        return policy

    except Exception as e:
        db.session.rollback()
        raise