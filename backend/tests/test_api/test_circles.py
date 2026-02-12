import json
from app.models import MoneyCircle, User

def test_create_money_circle(client, init_database):
    """Test successfully creating a new money circle."""
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    res = client.post('/api/circles/', headers=headers, json={
        "name": "Monthly Savings Club",
        "contribution_amount": "100.00"
    })
    
    assert res.status_code == 201
    assert "Money circle created" in res.get_json()['message']
    
    # Verify the creator is a member
    circle = MoneyCircle.query.filter_by(name="Monthly Savings Club").first()
    user1 = User.query.filter_by(email='user1@test.com').first()
    assert circle is not None
    assert user1 in circle.members

def test_get_user_money_circles(client, init_database):
    """Test getting the list of circles a user belongs to."""
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Create a circle first
    client.post('/api/circles/', headers=headers, json={
        "name": "Friends Circle", "contribution_amount": "50"
    })

    res = client.get('/api/circles/', headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'Friends Circle'
    assert data[0]['member_count'] == 1