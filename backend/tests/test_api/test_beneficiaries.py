import json

def test_add_beneficiary(client, init_database):
    """Test successfully adding a new beneficiary."""
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # User1 adds User2 as a beneficiary
    res = client.post('/api/beneficiaries/', headers=headers, json={
        "phone": "2222222222", # User2's phone
        "nickname": "Best Friend"
    })
    
    assert res.status_code == 201
    assert res.get_json()['message'] == "Beneficiary added successfully"

def test_get_beneficiaries(client, init_database):
    """Test retrieving the list of beneficiaries for a user."""
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Add a beneficiary first
    client.post('/api/beneficiaries/', headers=headers, json={"phone": "2222222222", "nickname": "Friend"})
    
    # Get the list
    res = client.get('/api/beneficiaries/', headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['nickname'] == 'Friend'
    assert data[0]['beneficiary_user']['phone'] == '2222222222'

def test_add_self_as_beneficiary_fails(client, init_database):
    """Test that a user cannot add themselves as a beneficiary."""
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    res = client.post('/api/beneficiaries/', headers=headers, json={
        "phone": "1111111111", # User1's own phone
        "nickname": "Myself"
    })
    assert res.status_code == 400
    assert "You cannot add yourself as a beneficiary" in res.get_json()['message']
    