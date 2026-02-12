import pytest
from decimal import Decimal
from app.services.wallet_service import deposit_to_wallet, withdraw_from_wallet
from app.utils.exceptions import InvalidUsage
from app.models import User

def test_deposit_to_wallet(client, init_database):
    """Test successfully depositing funds into a wallet."""
    user = User.query.filter_by(email='user1@test.com').first()
    initial_balance = user.wallet.balance
    
    deposit_amount = Decimal("50.50")
    updated_wallet = deposit_to_wallet(user.id, deposit_amount)
    
    assert updated_wallet.balance == initial_balance + deposit_amount

def test_withdraw_from_wallet_success(client, init_database):
    """Test a successful withdrawal."""
    user = User.query.filter_by(email='user1@test.com').first()
    initial_balance = user.wallet.balance
    
    withdrawal_amount = Decimal("25.00")
    updated_wallet = withdraw_from_wallet(user.id, withdrawal_amount)
    
    assert updated_wallet.balance == initial_balance - withdrawal_amount

def test_withdraw_from_wallet_insufficient_funds(client, init_database):
    """Test that withdrawing more than the balance raises an error."""
    user = User.query.filter_by(email='user1@test.com').first()
    
    with pytest.raises(InvalidUsage, match="Insufficient funds for withdrawal"):
        withdraw_from_wallet(user.id, Decimal("200.00")) # User only has 100