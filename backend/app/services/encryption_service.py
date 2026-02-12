from cryptography.fernet import Fernet
from flask import current_app

# In a real app, this key would be loaded securely, e.g., from a secrets manager.
# For this project, we'll load it from the app config.
# Ensure you generate a key by running: Fernet.generate_key()
# and add it to your .env file as ENCRYPTION_KEY.

def get_cipher():
    """Initializes and returns the Fernet cipher suite."""
    key = current_app.config['ENCRYPTION_KEY']
    if not key:
        raise ValueError("ENCRYPTION_KEY is not set in the application configuration.")
    return Fernet(key.encode())

def encrypt_data(data: str) -> str:
    """Encrypts a string and returns it as a URL-safe string."""
    if not data:
        return ""
    cipher = get_cipher()
    encrypted_text = cipher.encrypt(data.encode())
    return encrypted_text.decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypts a string and returns the original text."""
    if not encrypted_data:
        return ""
    cipher = get_cipher()
    try:
        decrypted_text = cipher.decrypt(encrypted_data.encode())
        return decrypted_text.decode()
    except Exception:
        # Handle cases where the token is invalid or tampered with
        return "Decryption failed. Invalid token."