import json

def test_get_user_profile_success(client, init_database):
    """
    Test that an authenticated user can successfully fetch their profile.
    """
    # 1. Log in as a user to get a valid token
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Make a request to the profile endpoint
    res = client.get('/api/users/profile', headers=headers)
    assert res.status_code == 200

    # 3. Verify the profile data in the response
    profile_data = res.get_json()
    assert profile_data['email'] == 'user1@test.com'
    assert profile_data['first_name'] == 'Test'
    assert profile_data['phone'] == '1111111111'
    assert 'id' in profile_data
    assert 'trust_score' in profile_data

def test_get_user_profile_unauthorized(client):
    """
    Test that an unauthenticated request to the profile endpoint fails.
    """

    # Make a request without an Authorization header
    res = client.get('/api/users/profile')
    
    # Assert that the request was unauthorized
    assert res.status_code == 401
    assert "Missing Authorization Header" in res.get_json()['msg']

def test_get_user_qr_code_success(client, init_database):
    """
    Test that an authenticated user can successfully generate a QR code.
    """
    # 1. Log in as a user to get a valid token
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Make a request to the QR code endpoint
    res = client.get('/api/users/qr-code', headers=headers)
    assert res.status_code == 200

    # 3. Verify the response format
    qr_data = res.get_json()
    assert 'qr_code' in qr_data
    
    # Check if the returned string is a valid base64 data URI for a PNG image
    qr_code_string = qr_data['qr_code']
    assert qr_code_string.startswith("data:image/png;base64,")
    # A simple check to ensure the base64 string is not empty
    assert len(qr_code_string) > 50