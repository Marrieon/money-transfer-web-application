import json

def test_regular_user_cannot_access_admin_routes(client, init_database):
    """
    Test that a non-admin user receives a 401 Unauthorized error for all admin endpoints.
    """
    # 1. Log in as a regular user
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Attempt to access admin route
    res = client.get('/api/admin/users', headers=headers)

    # DEBUG PRINT
    if res.status_code != 401:
        print(f"\n[DEBUG] Status: {res.status_code}")
        print(f"[DEBUG] Body: {res.get_json()}")

    # 3. Assert unauthorized
    assert res.status_code == 401

def test_admin_can_get_user_list(client, init_database):
    """
    Test that an authenticated admin user can successfully fetch the list of all users.
    """
    # 1. Log in as an admin
    login_res = client.post('/api/auth/login', json={'email': 'admin@test.com', 'password': 'adminpass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Access the /users endpoint
    res = client.get('/api/admin/users', headers=headers)
    
    # DEBUG PRINT
    if res.status_code != 200:
        print(f"\n[DEBUG] Status: {res.status_code}")
        print(f"[DEBUG] Body: {res.get_json()}")

    assert res.status_code == 200
    
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) >= 3

def test_admin_can_get_transaction_list(client, init_database):
    # Setup data
    user1_login = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    user1_token = user1_login.get_json()['access_token']
    client.post('/api/transactions/transfer', headers={'Authorization': f'Bearer {user1_token}'}, json={
        'receiver_phone': '2222222222', 'amount': '25.00'
    })

    # Admin login
    login_res = client.post('/api/auth/login', json={'email': 'admin@test.com', 'password': 'adminpass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    res = client.get('/api/admin/transactions', headers=headers)
    assert res.status_code == 200

def test_admin_can_get_stats(client, init_database):
    # Setup data
    user1_login = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    user1_token = user1_login.get_json()['access_token']
    client.post('/api/transactions/transfer', headers={'Authorization': f'Bearer {user1_token}'}, json={
        'receiver_phone': '2222222222', 'amount': '50.00'
    })

    # Admin login
    login_res = client.post('/api/auth/login', json={'email': 'admin@test.com', 'password': 'adminpass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    res = client.get('/api/admin/stats', headers=headers)
    assert res.status_code == 200
