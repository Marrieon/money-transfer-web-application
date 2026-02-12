import json
from decimal import Decimal

def test_get_wallet_success(client, init_database):
    """
    Test that an authenticated user can successfully fetch their wallet details.
    """
    # 1. Log in as user1 to get a valid token
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Make a request to the wallet endpoint
    res = client.get('/api/wallets/', headers=headers)
    assert res.status_code == 200

    # 3. Verify the wallet data
    wallet_data = res.get_json()
    assert wallet_data['currency'] == 'USD'
    # The init_database fixture gives user1 a balance of 100
    assert wallet_data['balance'] == 100.0
    assert wallet_data['status'] == 'active'

def test_deposit_to_wallet_success(client, init_database):
    """
    Test that a user can successfully deposit funds into their wallet.
    """
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Make a POST request to the /deposit action endpoint
    res = client.post('/api/wallets/deposit', headers=headers, json={'amount': '50.25'})
    assert res.status_code == 200

    # Verify the response message and new balance
    response_data = res.get_json()
    assert response_data['message'] == 'Deposit successful'
    # Initial balance was 100, new balance should be 150.25
    assert response_data['new_balance'] == 150.25

def test_withdraw_from_wallet_success(client, init_database):
    """
    Test that a user can successfully withdraw funds from their wallet.
    """
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Make a POST request to the /withdraw action endpoint
    res = client.post('/api/wallets/withdraw', headers=headers, json={'amount': '25.00'})
    assert res.status_code == 200

    # Verify the response message and new balance
    response_data = res.get_json()
    assert response_data['message'] == 'Withdraw successful'
    # Initial balance was 100, new balance should be 75.00
    assert response_data['new_balance'] == 75.0

def test_withdraw_insufficient_funds(client, init_database):
    """
    Test that the API returns an error if a user tries to withdraw more than their balance.
    """
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # User1 has 100, attempts to withdraw 200
    res = client.post('/api/wallets/withdraw', headers=headers, json={'amount': '200.00'})
    
    # Expect a 400 Bad Request error
    assert res.status_code == 400
    assert "Insufficient funds for withdrawal" in res.get_json()['message']

def test_wallet_invalid_action(client, init_database):
    """
    Test that using an invalid action in the URL returns an error.
    """
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Make a POST request to an undefined action like /invest
    res = client.post('/api/wallets/invest', headers=headers, json={'amount': '10.00'})
    
    assert res.status_code == 400
    assert "Invalid action" in res.get_json()['message']