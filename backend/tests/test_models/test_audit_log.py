from app.models import AuditLog, User
from app.extensions import db

def test_audit_log_creation(client, init_database):
    """
    Test that an AuditLog record can be successfully created and committed to the database.
    """
    # Get a user from our test fixture to associate with the log
    user = User.query.filter_by(email='user1@test.com').first()
    assert user is not None
    
    # 1. Create a new AuditLog instance
    audit_log = AuditLog(
        user_id=user.id,
        action='user_login_success',
        details={'ip_address': '127.0.0.1', 'user_agent': 'pytest'}
    )
    
    # 2. Add it to the session and commit
    db.session.add(audit_log)
    db.session.commit()
    
    # 3. Verify the record was created
    assert audit_log.id is not None
    
    # 4. Fetch the record from the database to confirm persistence
    retrieved_log = db.session.get(AuditLog, audit_log.id)
    assert retrieved_log is not None
    assert retrieved_log.action == 'user_login_success'
    assert retrieved_log.details['ip_address'] == '127.0.0.1'

def test_audit_log_user_relationship(client, init_database):
    """
    Test the relationship between the AuditLog and User models.
    """
    user = User.query.filter_by(email='user1@test.com').first()
    
    # Create a log associated with the user
    audit_log = AuditLog(
        user_id=user.id,
        action='profile_update'
    )
    db.session.add(audit_log)
    db.session.commit()
    
    # 1. Test the relationship from the AuditLog side
    # Fetch the log and check its '.user' attribute
    retrieved_log = db.session.get(AuditLog, audit_log.id)
    assert retrieved_log.user is not None
    assert retrieved_log.user.id == user.id
    assert retrieved_log.user.email == 'user1@test.com'
    
    # 2. Test that a system-level event (no user) can be created
    system_log = AuditLog(
        user_id=None,
        action='system_startup'
    )
    db.session.add(system_log)
    db.session.commit()
    
    retrieved_system_log = db.session.get(AuditLog, system_log.id)
    assert retrieved_system_log is not None
    assert retrieved_system_log.user_id is None
    assert retrieved_system_log.user is None