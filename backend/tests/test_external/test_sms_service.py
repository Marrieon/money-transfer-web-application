from unittest.mock import patch
from app.api.external.sms_service import send_sms

# We use @patch to replace the Twilio Client with a mock object during the test
@patch('app.api.external.sms_service.Client')
def test_send_sms_success(MockTwilioClient, app):
    """Test the send_sms function by mocking the Twilio client."""
    # Set fake credentials in the app config for this test
    app.config['TWILIO_ACCOUNT_SID'] = 'fake_sid'
    app.config['TWILIO_AUTH_TOKEN'] = 'fake_token'
    app.config['TWILIO_PHONE_NUMBER'] = '+15551234567'

    # Get the mock instance that the patch created
    mock_client_instance = MockTwilioClient.return_value
    # Set a return value for the 'create' method to simulate a successful API call
    mock_client_instance.messages.create.return_value.sid = "SMxxxxxxxxxxxxxx"

    # Call our service function
    sid = send_sms(to_phone="+15559876543", message="Hello from test")

    # Assert that the Twilio client was initialized correctly
    MockTwilioClient.assert_called_with('fake_sid', 'fake_token')
    
    # Assert that the 'create' method was called with the right parameters
    mock_client_instance.messages.create.assert_called_with(
        body="Hello from test",
        from_='+15551234567',
        to='+15559876543'
    )
    
    # Assert our function returned the SID
    assert sid == "SMxxxxxxxxxxxxxx"