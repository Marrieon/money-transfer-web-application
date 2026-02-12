import pytest
from app.services.auth_service import register_user, authenticate_user
from app.utils.exceptions import InvalidUsage
from app.models import User

def test_register_user_success(client, init_database):
    """
    Test that a new user can be successfully registered using the service.
    """
    # Define the new user's details
    new_user_data = {
        "email": "new@example.com",
        "phone": "1234567890",
        "password": "password123",
        "first_name": "New",
        "last_name": "User"
    }
    
    # Call the service function to register the user
    new_user = register_user(**new_user_data)
    
    # Assert that a user object was returned
    assert new_user is not None
    assert new_user.email == new_user_data["email"]
    
    # Verify the user exists in the database session
    # Note: We don't need to commit here because the test function's context handles it.
    db_user = User.query.filter_by(email=new_user_data["email"]).first()
    assert db_user is not None
    # Check that the password was hashed correctly
    assert db_user.check_password(new_user_data["password"])

def test_register_user_duplicate_email(client, init_database):
    """
    Test that the service prevents registration with a duplicate email
    and raises the correct exception.
    """
    # We expect an InvalidUsage exception to be raised
    with pytest.raises(InvalidUsage, match="User with this email or phone already exists"):
        # Attempt to register with an email that already exists from the init_database fixture
        register_user(
            email="user1@test.com", 
            phone="9876543210",
            password="password123",
            first_name="Duplicate",
            last_name="User"
        )

def test_authenticate_user_success(client, init_database):
    """
    Test that a user with correct credentials can be authenticated
    and receives a JWT token.
    """
    # Attempt to authenticate the user created in the init_database fixture
    token = authenticate_user("user1@test.com", "user1pass")
    
    # Assert that a token was returned and it is a string
    assert token is not None
    assert isinstance(token, str)

def test_authenticate_user_failure(client, init_database):
    """

    Test that a user with incorrect credentials cannot be authenticated
    and the function returns None.
    """
    # Attempt to authenticate with a wrong password
    token = authenticate_user("user1@test.com", "wrongpassword")
    
    # Assert that no token was returned
    assert token is None