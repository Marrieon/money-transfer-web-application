from decimal import Decimal
from app.models import Wallet, User
from app.extensions import db

def test_wallet_creation(client):
    """
    Test that a new Wallet can be created with its default values.
    """
    # 1. First, create a User to associate the wallet with
    user = User(
        email="walletowner@example.com",
        phone="5555555555",
        first_name="Wallet",
        last_name="Owner"
    )
    user.set_password("password")
    db.session.add(user)
    # We must commit the user first to get a user.id for the foreign key
    db.session.commit()

    # 2. Create a new Wallet instance
    wallet = Wallet(user_id=user.id)
    
    # 3. Add and commit to the database
    db.session.add(wallet)
    db.session.commit()

    # 4. Verify the wallet was created and has an ID
    assert wallet.id is not None

    # 5. Fetch the wallet and check its attributes and default values
    retrieved_wallet = db.session.get(Wallet, wallet.id)
    assert retrieved_wallet is not None
    assert retrieved_wallet.user_id == user.id
    assert retrieved_wallet.currency == 'USD'
    assert retrieved_wallet.balance == Decimal("0.0000")
    assert retrieved_wallet.status == 'active'

def test_wallet_user_relationship(client):
    """
    Test the relationship and back-population between Wallet and User.
    """
    # 1. Create a User and a Wallet in one go
    user = User(
        email="walletuser@example.com",
        phone="1212121212",
        first_name="Wallet",
        last_name="User"
    )
    user.set_password("password")
    wallet = Wallet(user=user) # Associate using the relationship, not the id
    
    db.session.add(user)
    db.session.add(wallet)
    db.session.commit()

    # 2. Test the forward relationship from the wallet to the user
    retrieved_wallet = db.session.get(Wallet, wallet.id)
    assert retrieved_wallet.user is not None
    assert retrieved_wallet.user.email == "walletuser@example.com"

    # 3. Test the back-populated relationship from the user to the wallet
    retrieved_user = db.session.get(User, user.id)
    assert retrieved_user.wallet is not None
    assert retrieved_user.wallet.id == wallet.id
    assert retrieved_user.wallet.currency == "USD"