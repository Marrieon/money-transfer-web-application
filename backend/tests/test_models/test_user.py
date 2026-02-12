import pytest
from sqlalchemy.exc import IntegrityError
from app.models import User
from app.extensions import db

def test_user_creation(client):
    """
    Test that a new User can be created with its default values.
    """
    # 1. Create a new User instance
    user = User(
        email="testuser@example.com",
        phone="1234567890",
        first_name="Test",
        last_name="User"
    )
    # We must set the password as the field is not nullable
    user.set_password("password123")
    
    # 2. Add and commit to the database
    db.session.add(user)
    db.session.commit()
    
    # 3. Verify the user was created and has an ID
    assert user.id is not None
    
    # 4. Fetch the user and check attributes
    retrieved_user = db.session.get(User, user.id)
    assert retrieved_user.email == "testuser@example.com"
    
    # Check all the default values
    assert retrieved_user.kyc_level == 0
    assert retrieved_user.trust_score == 50.0
    assert retrieved_user.is_admin is False

def test_password_hashing_and_checking(client):
    """
    Test the set_password and check_password methods.
    """
    user = User(
        email="passwordtest@example.com",
        phone="0987654321",
        first_name="Password",
        last_name="Test"
    )
    
    # Set the password
    user.set_password("a-very-secure-password")
    
    # 1. The password_hash should not be the same as the plain text password
    assert user.password_hash is not None
    assert user.password_hash != "a-very-secure-password"
    
    # 2. check_password should return True for the correct password
    assert user.check_password("a-very-secure-password") is True
    
    # 3. check_password should return False for an incorrect password
    assert user.check_password("wrong-password") is False

def test_user_email_uniqueness(client, init_database):
    """
    Test that the database unique constraint on the email field is working.
    """
    # 1. Get an existing user from the fixture
    existing_user = User.query.filter_by(email='user1@test.com').first()
    
    # 2. Create a new user with the SAME email
    duplicate_user = User(
        email=existing_user.email,
        phone="1112223333",
        first_name="Duplicate",
        last_name="Email"
    )
    duplicate_user.set_password("password")
    db.session.add(duplicate_user)
    
    # 3. Expect an IntegrityError when trying to commit
    with pytest.raises(IntegrityError):
        db.session.commit()

def test_user_phone_uniqueness(client, init_database):
    """
    Test that the database unique constraint on the phone field is working.
    """
    # Rollback session in case the previous test failed and left it in a bad state
    db.session.rollback()
    
    # 1. Get an existing user from the fixture
    existing_user = User.query.filter_by(phone='1111111111').first()
    
    # 2. Create a new user with the SAME phone number
    duplicate_user = User(
        email="duplicatephone@example.com",
        phone=existing_user.phone,
        first_name="Duplicate",
        last_name="Phone"
    )
    duplicate_user.set_password("password")
    db.session.add(duplicate_user)
    
    # 3. Expect an IntegrityError when trying to commit
    with pytest.raises(IntegrityError):
        db.session.commit()