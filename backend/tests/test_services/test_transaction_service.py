from app.services import encryption_service

def test_encryption_decryption_cycle(app):
    """Test that data can be encrypted and then decrypted back to the original."""
    # Set a dummy key in the app config for this test
    app.config['ENCRYPTION_KEY'] = 'a2L7jVixM21kexXm2-s2_c8-h9UuB_zG4eAbCdEfG1o='
    
    original_data = "This is a secret message with account number 12345."
    
    # Encrypt the data
    encrypted_data = encryption_service.encrypt_data(original_data)
    
    # Assert that the encrypted data is different from the original
    assert encrypted_data is not None
    assert original_data not in encrypted_data
    
    # Decrypt the data
    decrypted_data = encryption_service.decrypt_data(encrypted_data)
    
    # Assert that the decrypted data matches the original
    assert decrypted_data == original_data

def test_decryption_failure(app):
    """Test that decrypting a tampered or invalid token fails gracefully."""
    app.config['ENCRYPTION_KEY'] = 'a2L7jVixM21kexXm2-s2_c8-h9UuB_zG4eAbCdEfG1o='
    
    invalid_token = "this-is-not-a-valid-fernet-token"
    
    decrypted_data = encryption_service.decrypt_data(invalid_token)
    
    assert decrypted_data == "Decryption failed. Invalid token."