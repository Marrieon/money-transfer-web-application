import json

def test_register(client):
    """Test user registration."""
    res = client.post('/api/auth/register', data=json.dumps({
        "email": "newuser@test.com",
        "phone": "3333333333",
        "password": "newpassword",
        "first_name": "New",
        "last_name": "User"
    }), content_type='application/json')
    assert res.status_code == 201
    assert "User created successfully" in res.get_json()['message']

def test_login(client, init_database):
    """Test user login."""
    res = client.post('/api/auth/login', data=json.dumps({
        "email": "user1@test.com",
        "password": "user1pass"
    }), content_type='application/json')
    assert res.status_code == 200
    assert 'access_token' in res.get_json()

def test_login_invalid_password(client, init_database):
    """Test login with wrong password."""
    res = client.post('/api/auth/login', data=json.dumps({
        "email": "user1@test.com",
        "password": "wrongpassword"
    }), content_type='application/json')
    assert res.status_code == 400
    assert "Invalid email or password" in res.get_json()['message']