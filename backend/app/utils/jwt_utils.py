from flask_jwt_extended import get_jwt_identity
from app.utils.exceptions import Unauthorized


def get_current_user_id():
    identity = get_jwt_identity()
    if identity is None:
        raise Unauthorized("Missing user identity")
    try:
        return int(identity)
    except (TypeError, ValueError):
        raise Unauthorized("Invalid user identity")
