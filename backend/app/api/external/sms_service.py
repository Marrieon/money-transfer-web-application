from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from flask import current_app

def send_sms(to_phone: str, message: str) -> str:
    """
    Sends an SMS message using the Twilio API.
    """
    account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
    auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
    from_phone = current_app.config.get('TWILIO_PHONE_NUMBER')

    if not all([account_sid, auth_token, from_phone]):
        current_app.logger.warning("Twilio is not configured. SMS not sent.")
        return "not_configured"

    # Add '+' to phone number if it's not there, required by Twilio
    if not to_phone.startswith('+'):
        # This assumes a country code should be added, which you might make more robust
        # For now, we'll assume numbers are stored with a country code but no '+'
        to_phone = f"+{to_phone}"

    try:
        client = Client(account_sid, auth_token)
        message_instance = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        current_app.logger.info(f"SMS sent successfully to {to_phone}, SID: {message_instance.sid}")
        return message_instance.sid
    except TwilioRestException as e:
        current_app.logger.error(f"Failed to send SMS to {to_phone}: {e}")
        return "failed"