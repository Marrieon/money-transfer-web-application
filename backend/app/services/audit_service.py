from app.extensions import db
from app.models.audit_log import AuditLog


def log_action(action: str, user_id: int = None, details: dict = None):
    """Helper function to create an audit log entry."""
    audit_log = AuditLog(user_id=user_id, action=action, details=details)
    db.session.add(audit_log)
    # Note: This relies on an external commit. 
    # For critical logs, you might want to commit immediately.