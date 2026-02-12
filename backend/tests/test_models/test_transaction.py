from decimal import Decimal
from app.models import Transaction, User
from app.extensions import db

def test_transaction_creation(client, init_database):
    """
    Test that a Transaction can be created with its default values.
    """
    # Get the sender (user1) and receiver (user2) from the test fixture
    sender = User.query.filter_by(email='user1@test.com').first()
    receiver = User.query.filter_by(email='user2@test.com').first()
    
    # 1. Create a new Transaction instance
    tx = Transaction(
        sender_id=sender.id,
        receiver_id=receiver.id,
        amount=Decimal("125.50"),
        type='transfer' # A non-defaulted, required field
    )
    
    # 2. Add and commit to the database
    db.session.add(tx)
    db.session.commit()
    
    # 3. Verify the record was created and has an ID
    assert tx.id is not None
    
    # 4. Fetch the record and check its attributes
    retrieved_tx = db.session.get(Transaction, tx.id)
    assert retrieved_tx is not None
    assert retrieved_tx.sender_id == sender.id
    assert retrieved_tx.receiver_id == receiver.id
    assert retrieved_tx.amount == Decimal("125.5000")
    
    # Check all the default values
    assert retrieved_tx.currency == 'USD'
    assert retrieved_tx.fee == Decimal("0.0000")
    assert retrieved_tx.status == 'pending'
    assert retrieved_tx.category == 'Uncategorized'

def test_transaction_relationships(client, init_database):
    """
    Test that the 'sender' and 'receiver' relationships and their back-population work correctly.
    """
    sender = User.query.filter_by(email='user1@test.com').first()
    receiver = User.query.filter_by(email='user2@test.com').first()
    
    # Create two transactions to test list relationships
    tx1 = Transaction(sender_id=sender.id, receiver_id=receiver.id, amount=Decimal("10.00"), type='transfer')
    tx2 = Transaction(sender_id=sender.id, receiver_id=receiver.id, amount=Decimal("20.00"), type='transfer')
    
    db.session.add_all([tx1, tx2])
    db.session.commit()
    
    # Fetch a transaction and test the forward relationships
    retrieved_tx = db.session.get(Transaction, tx1.id)
    assert retrieved_tx.sender is not None
    assert retrieved_tx.sender.email == sender.email
    assert retrieved_tx.receiver is not None
    assert retrieved_tx.receiver.email == receiver.email
    
    # Test the back-population from the User side
    # We must refresh the user objects to load the new relationship data
    db.session.refresh(sender)
    db.session.refresh(receiver)
    
    # Sender should have two sent transactions and zero received
    assert len(sender.transactions_sent.all()) == 2
    assert len(sender.transactions_received.all()) == 0
    assert tx1 in sender.transactions_sent.all()
    
    # Receiver should have two received transactions and zero sent
    assert len(receiver.transactions_received.all()) == 2
    assert len(receiver.transactions_sent.all()) == 0
    assert tx1 in receiver.transactions_received.all()