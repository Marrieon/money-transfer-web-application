from decimal import Decimal # NEW: Import Decimal
from app.extensions import db
from app.models import User, Merchant, Wallet, Transaction
from app.utils.exceptions import InvalidUsage, NotFound

def create_merchant_account(user_id: int, business_name: str):
    """Creates a new merchant account for a user."""
    if not business_name:
        raise InvalidUsage("Business name is required.")
        
    user = db.session.get(User, user_id)
    if not user:
        raise NotFound("User not found.")

    existing_merchant = Merchant.query.filter_by(user_id=user_id).first()
    if existing_merchant:
        raise InvalidUsage("User already has a merchant account.")

    merchant = Merchant(user_id=user_id, business_name=business_name)
    db.session.add(merchant)
    db.session.commit()
    
    return merchant

def process_merchant_payment(api_key: str, amount: float, customer_phone: str):
    """Processes a payment from a customer to a merchant."""
    merchant = Merchant.query.filter_by(api_key=api_key, is_active=True).first()
    if not merchant:
        raise NotFound("Invalid or inactive merchant API key.")
        
    customer = User.query.filter_by(phone=customer_phone).first()
    if not customer:
        raise NotFound("Customer with this phone number not found.")

    merchant_user = merchant.user
    
    # Use the existing create_transfer function for consistency
    from .transaction_service import create_transfer
    
    # MODIFIED (The Fix): Convert the incoming amount to a Decimal object
    # to maintain high precision throughout the transaction process.
    try:
        decimal_amount = Decimal(str(amount))
    except:
        raise InvalidUsage("Invalid amount format.")

    transaction = create_transfer(
        sender_id=customer.id,
        receiver_phone=merchant_user.phone,
        amount=decimal_amount # Pass the Decimal object here
    )

    # Re-categorize the transaction for better analytics
    transaction.type = 'merchant_payment'
    transaction.category = 'Goods & Services'
    db.session.commit()

    return transaction