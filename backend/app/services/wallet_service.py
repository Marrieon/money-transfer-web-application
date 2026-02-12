
from decimal import Decimal
from app.extensions import db
from app.models import User, SavingsGoal, Transaction
from app.utils.exceptions import InvalidUsage, NotFound

def deposit_to_wallet(user_id: int, amount: Decimal):
    """Adds funds to a user's main wallet."""
    if amount <= 0:
        raise InvalidUsage("Deposit amount must be positive.")
        
    user = db.session.get(User, user_id)
    if not user or not user.wallet:
        raise NotFound("User or wallet not found.")
        
    user.wallet.balance += amount
    
    transaction = Transaction(
        sender_id=user_id,
        receiver_id=user_id, # Self-transaction
        amount=amount,
        fee=0,
        status='completed',
        type='deposit',
        category='Income'
    )
    db.session.add(transaction)
    return user.wallet

def withdraw_from_wallet(user_id: int, amount: Decimal):
    """Withdraws funds from a user's main wallet."""
    if amount <= 0:
        raise InvalidUsage("Withdrawal amount must be positive.")
    
    user = db.session.get(User, user_id)
    if not user or not user.wallet:
        raise NotFound("User or wallet not found.")
    
    if user.wallet.balance < amount:
        raise InvalidUsage("Insufficient funds for withdrawal.")
        
    user.wallet.balance -= amount
    
    transaction = Transaction(
        sender_id=user_id,
        receiver_id=user_id, # Self-transaction
        amount=amount,
        fee=0,
        status='completed',
        type='withdrawal',
        category='Withdrawals'
    )
    db.session.add(transaction)
    return user.wallet

def transfer_to_savings_goal(user_id: int, goal_id: int, amount: Decimal):
    """Transfers money from a user's main wallet to their savings goal."""
    if amount <= 0:
        raise InvalidUsage("Deposit amount must be positive.")

    user = db.session.get(User, user_id)
    goal = db.session.get(SavingsGoal, goal_id)

    if not user or not user.wallet:
        raise NotFound("User or wallet not found.")
    if not goal or goal.user_id != user_id:
        raise NotFound("Savings goal not found or does not belong to user.")
    
    if user.wallet.balance < amount:
        raise InvalidUsage("Insufficient funds in main wallet.")

    user.wallet.balance -= amount
    goal.current_amount += amount

    transaction = Transaction(
        sender_id=user_id,
        receiver_id=user_id,
        amount=amount,
        fee=0,
        status='completed',
        type='savings_deposit',
        category='Savings'
    )
    db.session.add(transaction)
    return goal