from decimal import Decimal
from app.extensions import db
from app.models import User, Wallet, Transaction, Beneficiary
from app.utils.exceptions import InvalidUsage, NotFound, APIException
from app.services.notification_service import create_notification
from app.services.trust_service import update_trust_score
from app.services.fraud_detection import check_for_fraud
# NEW: Import the exchange rate service
from app.api.external.exchange_rates import get_exchange_rate


def _calculate_fee(amount: Decimal) -> Decimal:
    """Calculates the transaction fee based on amount."""
    if amount < 10:
        return Decimal('0.00')
    elif 10 <= amount <= 100:
        return amount * Decimal('0.005')
    else:
        return amount * Decimal('0.01')


def create_transfer(sender_id: int, receiver_phone: str, amount: Decimal):
    """Handles a standard, single-currency peer-to-peer transfer."""
    if amount <= 0:
        raise InvalidUsage("Transfer amount must be positive.")

    sender = db.session.get(User, sender_id)
    receiver = User.query.filter_by(phone=receiver_phone).first()

    if not sender or not receiver:
        raise NotFound("Sender or receiver not found.")
    if sender.id == receiver.id:
        raise InvalidUsage("Cannot send money to yourself.")
    if not sender.wallet or not receiver.wallet:
        raise InvalidUsage("One of the users does not have a wallet.")

    is_new_beneficiary = not Beneficiary.query.filter_by(user_id=sender.id, beneficiary_user_id=receiver.id).first()
    if check_for_fraud(sender=sender, transaction_amount=amount, is_new_beneficiary=is_new_beneficiary):
        update_trust_score(sender_id, "fraud_attempt_blocked", -25)
        db.session.commit()
        raise InvalidUsage("This transaction has been flagged for a security review.")

    fee = _calculate_fee(amount)
    total_debit = amount + fee

    if sender.wallet.balance < total_debit:
        raise InvalidUsage("Insufficient funds.")
        
    try:
        sender.wallet.balance -= total_debit
        receiver.wallet.balance += amount
        
        transaction = Transaction(
            sender_id=sender.id, receiver_id=receiver.id, amount=amount,
            fee=fee, status='completed', type='transfer'
        )
        db.session.add(transaction)
        
        message = f"You have received {amount:.2f} {sender.wallet.currency} from {sender.first_name}."
        create_notification(receiver.id, message, 'transfer_received', send_sms_notification=True)
        
        update_trust_score(sender_id, "successful_transfer_sent", 1.5)
        update_trust_score(receiver.id, "successful_transfer_received", 1.0)
        
        db.session.commit()
        return transaction
    except Exception as e:
        db.session.rollback()
        raise APIException(f"Transaction failed: {str(e)}")


# NEW: The missing function that caused the crash
def create_multicurrency_transfer(sender_id: int, receiver_phone: str, send_amount: Decimal, target_currency: str):
    """Handles a transfer where the sent and received currencies are different."""
    sender = db.session.get(User, sender_id)
    receiver = User.query.filter_by(phone=receiver_phone).first()

    if not sender or not receiver:
        raise NotFound("Sender or receiver not found.")
    if not sender.wallet or not receiver.wallet:
        raise InvalidUsage("Sender or receiver does not have a wallet.")
    if send_amount <= 0:
        raise InvalidUsage("Amount must be positive.")

    base_currency = sender.wallet.currency
    if base_currency == target_currency:
        raise InvalidUsage("For same-currency transfers, use the standard /transfer endpoint.")
        
    rate = get_exchange_rate(base_currency, target_currency)
    if rate == 1.0:
        raise InvalidUsage("Could not retrieve a valid exchange rate for the requested currencies.")

    received_amount = send_amount * Decimal(str(rate))
    fee = _calculate_fee(send_amount)
    total_debit = send_amount + fee
    
    if sender.wallet.balance < total_debit:
        raise InvalidUsage("Insufficient funds.")

    try:
        sender.wallet.balance -= total_debit
        receiver.wallet.balance += received_amount
        receiver.wallet.currency = target_currency

        transaction = Transaction(
            sender_id=sender.id, receiver_id=receiver.id, amount=send_amount,
            currency=base_currency, fee=fee, status='completed',
            type='multicurrency_transfer', category='Cross-Border'
        )
        db.session.add(transaction)
        
        message = f"You have received {received_amount:.2f} {target_currency} from {sender.first_name}."
        create_notification(receiver.id, message, 'transfer_received', send_sms_notification=True)
        
        db.session.commit()
        return transaction
    except Exception as e:
        db.session.rollback()
        raise APIException(f"Transaction failed: {str(e)}")