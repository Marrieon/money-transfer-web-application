from functools import wraps
from flask_jwt_extended import verify_jwt_in_request
from app.models import User
from app.extensions import db # Import db
from .exceptions import Unauthorized
from .jwt_utils import get_current_user_id

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_current_user_id()
            # MODIFIED: Use modern db.session.get()
            user = db.session.get(User, user_id)
            if not user or not user.is_admin:
                raise Unauthorized("Admins only!")
            return fn(*args, **kwargs)
        return decorator
    return wrapper
