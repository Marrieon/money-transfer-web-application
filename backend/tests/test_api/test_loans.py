import json
from app.models import Loan, Notification

def test_request_loan(client, init_database):
    """Test a user successfully requesting a loan from another user."""
    # Borrower (user1) logs in
    login_res_borrower = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token_borrower = login_res_borrower.get_json()['access_token']
    headers_borrower = {'Authorization': f'Bearer {token_borrower}'}

    # User1 requests a loan from User2
    res = client.post('/api/loans/', headers=headers_borrower, json={
        "lender_phone": "2222222222", # User2's phone
        "amount": "250.00",
        "repayment_date": "2025-12-31"
    })

    assert res.status_code == 201
    assert "Loan requested successfully" in res.get_json()['message']

    # Verify loan was created with correct status
    loan = Loan.query.first()
    assert loan is not None
    assert loan.borrower_id == 2 # user1's id
    assert loan.lender_id == 3 # user2's id
    assert loan.status == 'requested'

    # Verify lender (user2) received a notification
    notification = Notification.query.filter_by(user_id=3, notification_type='loan_request').first()
    assert notification is not None
    assert "has requested a loan" in notification.message

def test_get_user_loans(client, init_database):
    """Test retrieving a user's lent and borrowed loans."""
    # User1 requests a loan from User2
    login_res_borrower = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token_borrower = login_res_borrower.get_json()['access_token']
    headers_borrower = {'Authorization': f'Bearer {token_borrower}'}
    client.post('/api/loans/', headers=headers_borrower, json={
        "lender_phone": "2222222222", "amount": "100", "repayment_date": "2025-01-01"
    })

    # User2 logs in to view loans
    login_res_lender = client.post('/api/auth/login', json={'email': 'user2@test.com', 'password': 'user2pass'})
    token_lender = login_res_lender.get_json()['access_token']
    headers_lender = {'Authorization': f'Bearer {token_lender}'}

    res = client.get('/api/loans/', headers=headers_lender)
    assert res.status_code == 200
    data = res.get_json()
    assert len(data['lent']) == 1
    assert len(data['borrowed']) == 0
    assert data['lent'][0]['borrower'] == 'user1@test.com'
    assert data['lent'][0]['status'] == 'requested'