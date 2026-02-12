import json
from app.models import AuditLog, User

def test_admin_stats(client, init_database):
    # Login as admin
    login_res = client.post('/api/auth/login', json={'email': 'admin@test.com', 'password': 'adminpass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Login as user1
    user1_login = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    user1_token = user1_login.get_json()['access_token']
    user1_headers = {'Authorization': f'Bearer {user1_token}'}

    # Perform a transaction
    client.post('/api/transactions/transfer', headers=user1_headers, json={
        'receiver_phone': '2222222222', 'amount': '15.00'
    })

    # Get admin stats
    res = client.get('/api/admin/stats', headers=headers)
    assert res.status_code == 200
    stats = res.get_json()
    assert stats['total_users'] == 3
    assert stats['total_transactions'] == 1
    assert stats['total_volume'] == 15.0
    assert stats['total_revenue'] > 0


def test_spending_summary(client, init_database):
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Perform a transaction
    client.post('/api/transactions/transfer', headers=headers, json={
        'receiver_phone': '2222222222', 'amount': '20.00'
    })

    # Fetch spending summary
    res = client.get('/api/analytics/spending-summary', headers=headers)
    assert res.status_code == 200
    summary = res.get_json()
    assert 'Uncategorized' in summary
    assert summary['Uncategorized'] == 20.0


def test_audit_log_on_login(client, init_database):
    initial_log_count = AuditLog.query.count()

    # Perform successful login
    client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})

    # Perform failed login
    client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'wrongpassword'})

    # Validate audit logs
    new_log_count = AuditLog.query.count()
    assert new_log_count == initial_log_count + 2

    # Validate successful login log
    success_log = AuditLog.query.filter_by(action='user_login_success').order_by(AuditLog.id.desc()).first()
    assert success_log is not None
    user = User.query.filter_by(email='user1@test.com').first()
    assert success_log.user_id == user.id

    # Validate failed login log
    fail_log = AuditLog.query.filter_by(action='user_login_failed').order_by(AuditLog.id.desc()).first()
    assert fail_log is not None
    assert fail_log.details.get('email') == 'user1@test.com'
