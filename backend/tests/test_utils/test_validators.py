import pytest
from app.utils.validators import is_valid_email, is_valid_phone

@pytest.mark.parametrize("email, expected", [
    ("test@example.com", True),
    ("test.user@example.co.uk", True),
    ("test@example", False),
    ("test.example.com", False),
    ("", False),
    (None, False)
])
def test_is_valid_email(email, expected):
    """Test the email validator with various inputs."""
    assert is_valid_email(email) == expected

@pytest.mark.parametrize("phone, expected", [
    ("1234567890", True),
    ("+11234567890", True),
    ("12345", False),
    ("123-456-7890", False),
    ("abcdefghij", False),
    ("", False),
    (None, False)
])
def test_is_valid_phone(phone, expected):
    """Test the phone number validator with various inputs."""
    assert is_valid_phone(phone) == expected