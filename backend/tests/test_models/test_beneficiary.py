import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Beneficiary, User
from app.extensions import db

def test_beneficiary_creation(client, init_database):
    """
    Test that a Beneficiary record can be successfully created.
    """
    # Get the owner (user1) and the beneficiary (user2) from the test fixture
    owner_user = User.query.filter_by(email='user1@test.com').first()
    beneficiary_user = User.query.filter_by(email='user2@test.com').first()
    
    # 1. Create a new Beneficiary instance
    beneficiary = Beneficiary(
        user_id=owner_user.id,
        beneficiary_user_id=beneficiary_user.id,
        nickname="Close Friend"
    )
    
    # 2. Add and commit to the database
    db.session.add(beneficiary)
    db.session.commit()
    
    # 3. Verify the record was created and has an ID
    assert beneficiary.id is not None
    
    # 4. Fetch the record and check its attributes
    retrieved_beneficiary = db.session.get(Beneficiary, beneficiary.id)
    assert retrieved_beneficiary is not None
    assert retrieved_beneficiary.nickname == "Close Friend"
    assert retrieved_beneficiary.user_id == owner_user.id
    assert retrieved_beneficiary.beneficiary_user_id == beneficiary_user.id

def test_beneficiary_relationships(client, init_database):
    """
    Test the 'owner' and 'beneficiary_user' relationships are correctly established.
    """
    owner_user = User.query.filter_by(email='user1@test.com').first()
    beneficiary_user = User.query.filter_by(email='user2@test.com').first()
    
    beneficiary = Beneficiary(
        user_id=owner_user.id,
        beneficiary_user_id=beneficiary_user.id,
        nickname="Work Colleague"
    )
    db.session.add(beneficiary)
    db.session.commit()
    
    # Fetch the record and test the relationships
    retrieved_beneficiary = db.session.get(Beneficiary, beneficiary.id)
    
    # Test the 'owner' relationship
    assert retrieved_beneficiary.owner is not None
    assert retrieved_beneficiary.owner.email == owner_user.email
    
    # Test the 'beneficiary_user' relationship
    assert retrieved_beneficiary.beneficiary_user is not None
    assert retrieved_beneficiary.beneficiary_user.email == beneficiary_user.email

def test_beneficiary_uniqueness_constraint(client, init_database):
    """
    Test that the database unique constraint prevents duplicate beneficiaries.
    """
    owner_user = User.query.filter_by(email='user1@test.com').first()
    beneficiary_user = User.query.filter_by(email='user2@test.com').first()
    
    # 1. Create the first, valid beneficiary record
    beneficiary1 = Beneficiary(
        user_id=owner_user.id,
        beneficiary_user_id=beneficiary_user.id,
        nickname="Friend"
    )
    db.session.add(beneficiary1)
    db.session.commit()
    
    # 2. Create a second, duplicate beneficiary record
    beneficiary2 = Beneficiary(
        user_id=owner_user.id,
        beneficiary_user_id=beneficiary_user.id, # Same owner and beneficiary
        nickname="Also A Friend"
    )
    db.session.add(beneficiary2)
    
    # 3. Expect an IntegrityError when trying to commit the duplicate
    # This confirms that our database-level constraint is working correctly.
    with pytest.raises(IntegrityError):
        db.session.commit()