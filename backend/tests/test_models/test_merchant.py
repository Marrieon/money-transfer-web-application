import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Merchant, User
from app.extensions import db

def test_merchant_creation(client, init_database):
    """
    Test that a Merchant record can be created with its default values.
    """
    # Get a user from the test fixture to create a merchant account for
    user = User.query.filter_by(email='user1@test.com').first()
    
    # 1. Create a new Merchant instance
    merchant = Merchant(
        user_id=user.id,
        business_name="Newton's Fine Wares"
    )
    
    # 2. Add and commit to the database
    db.session.add(merchant)
    db.session.commit()
    
    # 3. Verify the record was created and has an ID
    assert merchant.id is not None
    
    # 4. Fetch the record and check its attributes
    retrieved_merchant = db.session.get(Merchant, merchant.id)
    assert retrieved_merchant is not None
    assert retrieved_merchant.user_id == user.id
    assert retrieved_merchant.business_name == "Newton's Fine Wares"
    
    # Check the default values
    assert retrieved_merchant.is_active is True
    # Check that an API key was generated and is a non-empty string
    assert retrieved_merchant.api_key is not None
    assert isinstance(retrieved_merchant.api_key, str)
    assert len(retrieved_merchant.api_key) > 10

def test_merchant_user_relationship(client, init_database):
    """
    Test that the 'user' relationship is correctly linked.
    """
    user = User.query.filter_by(email='user1@test.com').first()
    
    merchant = Merchant(
        user_id=user.id,
        business_name="Test Shop"
    )
    db.session.add(merchant)
    db.session.commit()
    
    # Fetch the merchant record and test the relationship
    retrieved_merchant = db.session.get(Merchant, merchant.id)
    
    assert retrieved_merchant.user is not None
    assert retrieved_merchant.user.email == user.email

def test_merchant_user_id_uniqueness(client, init_database):
    """
    Test that a single user cannot have more than one merchant account.
    """
    user = User.query.filter_by(email='user1@test.com').first()
    
    # 1. Create the first, valid merchant account
    merchant1 = Merchant(
        user_id=user.id,
        business_name="Original Shop"
    )
    db.session.add(merchant1)
    db.session.commit()
    
    # 2. Create a second merchant account for the SAME user
    merchant2 = Merchant(
        user_id=user.id,
        business_name="Second Shop"
    )
    db.session.add(merchant2)
    
    # 3. Expect an IntegrityError when trying to commit the duplicate
    # This confirms the unique=True constraint on user_id is working.
    with pytest.raises(IntegrityError):
        db.session.commit()