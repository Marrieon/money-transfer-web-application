
import json
from app.models import Notification

def test_notification_on_transfer(client, init_database):
    """Test that a notification is created for the receiver upon a successful transfer."""
    # User1 logs in
    login_res_sender = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token_sender = login_res_sender.get_json()['access_token']
    headers_sender = {'Authorization': f'Bearer {token_sender}'}

    # User1 sends money to User2
    client.post('/api/transactions/transfer', headers=headers_sender, json={
        'receiver_phone': '2222222222',
        'amount': '10.00'
    })

    # Check User2's notifications
    notification = Notification.query.filter_by(user_id=3).first() # User2's ID is 3
    assert notification is not None
    assert "You have received 10.00" in notification.message
    assert notification.notification_type == 'transfer_received'
    assert not notification.is_read

def test_get_notifications(client, init_database):
    """Test retrieving a user's notifications."""
    # Create a notification for User2 manually for this test
    from app.services.notification_service import create_notification
    from app.extensions import db
    create_notification(user_id=3, message="Test notification", notification_type="test")
    db.session.commit()

    # User2 logs in
    login_res = client.post('/api/auth/login', json={'email': 'user2@test.com', 'password': 'user2pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    res = client.get('/api/notifications/', headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]['message'] == "Test notification"

def test_mark_notifications_as_read(client, init_database):
    """Test marking all of a user's notifications as read."""
    # Create a notification for User2
    from app.services.notification_service import create_notification
    from app.extensions import db
    create_notification(user_id=3, message="Unread message", notification_type="test")
    db.session.commit()
    
    # User2 logs in
    login_res = client.post('/api/auth/login', json={'email': 'user2@test.com', 'password': 'user2pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Mark as read
    res = client.post('/api/notifications/', headers=headers)
    assert res.status_code == 200

    # Verify it is marked as read
    notification = Notification.query.filter_by(user_id=3).first()
    assert notification.is_read is True