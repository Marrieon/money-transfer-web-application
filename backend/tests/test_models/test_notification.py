from app.models import Notification, User
from app.extensions import db

def test_notification_creation(client, init_database):
    """
    Test that a Notification record can be created with its default 'is_read' status.
    """
    # Get a user from the fixture to receive the notification
    user = User.query.filter_by(email='user1@test.com').first()
    
    # 1. Create a new Notification instance
    notification = Notification(
        user_id=user.id,
        message="You have received a payment of $50.00.",
        notification_type="transfer_received"
    )
    
    # 2. Add and commit to the database
    db.session.add(notification)
    db.session.commit()
    
    # 3. Verify the record was created and has an ID
    assert notification.id is not None
    
    # 4. Fetch the record and check its attributes
    retrieved_notification = db.session.get(Notification, notification.id)
    assert retrieved_notification is not None
    assert retrieved_notification.user_id == user.id
    assert retrieved_notification.message == "You have received a payment of $50.00."
    assert retrieved_notification.notification_type == "transfer_received"
    
    # Check the default value for 'is_read'
    assert retrieved_notification.is_read is False

def test_notification_user_relationship(client, init_database):
    """
    Test that the 'user' relationship is correctly linked.
    """
    user = User.query.filter_by(email='user2@test.com').first()
    
    notification = Notification(
        user_id=user.id,
        message="Your loan request has been approved.",
        notification_type="loan_approved"
    )
    db.session.add(notification)
    db.session.commit()
    
    # Fetch the notification and test the relationship
    retrieved_notification = db.session.get(Notification, notification.id)
    
    assert retrieved_notification.user is not None
    assert retrieved_notification.user.email == user.email