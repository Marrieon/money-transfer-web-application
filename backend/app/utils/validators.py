import re

def is_valid_email(email: str) -> bool:
    """Check if the email has a valid format."""
    if not email:
        return False
    # A simple regex for email validation
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone: str) -> bool:
    """Check if the phone number is valid (e.g., 10-15 digits)."""
    if not phone:
        return False
    # A simple regex for phone validation (allows for optional '+')
    pattern = r'^\+?[0-9]{10,15}$'
    return re.match(pattern, phone) is not None