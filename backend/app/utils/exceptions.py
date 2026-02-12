class APIException(Exception):
    """Base class for API-specific exceptions."""
    status_code = 500
    message = "An unexpected error occurred."

    def __init__(self, message=None, status_code=None, payload=None):
        # MODIFIED (The Fix): Pass the message to the parent Exception class.
        # This ensures that testing tools like pytest can correctly inspect the exception message.
        if message is not None:
            self.message = message
        super().__init__(self.message) # Pass the final message to the parent
        
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class InvalidUsage(APIException):
    status_code = 400

class NotFound(APIException):
    status_code = 404

class Unauthorized(APIException):
    status_code = 401