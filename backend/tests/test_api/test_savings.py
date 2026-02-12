import json
from decimal import Decimal
from app.models import SavingsGoal, Wallet
from app.extensions import db

def test_create_savings_goal(client, init_database):
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    res = client.post('/api/savings/goals', headers=headers, json={
        "title": "New Car Fund",
        "target_amount": "5000.00"
    })
    assert res.status_code == 201
    assert "Savings goal created" in res.get_json()['message']
    
    goal = SavingsGoal.query.filter_by(title="New Car Fund").first()
    assert goal is not None
    assert goal.user_id == 2

def test_get_savings_goals(client, init_database):
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    client.post('/api/savings/goals', headers=headers, json={
        "title": "Vacation", "target_amount": "1200"
    })

    res = client.get('/api/savings/goals', headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['title'] == 'Vacation'

def test_deposit_to_savings_goal(client, init_database):
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    create_res = client.post('/api/savings/goals', headers=headers, json={
        "title": "Gadget", "target_amount": "800"
    })
    goal_id = create_res.get_json()['id']

    res = client.post(f'/api/savings/goals/{goal_id}/deposit', headers=headers, json={
        "amount": "50.75"
    })
    assert res.status_code == 200
    assert res.get_json()['message'] == 'Deposit successful'

    # MODIFIED: Use modern db.session.get() to remove warning
    goal = db.session.get(SavingsGoal, goal_id)
    wallet = Wallet.query.filter_by(user_id=2).first()
    assert goal.current_amount == Decimal('50.7500')
    assert wallet.balance == Decimal('100.0000') - Decimal('50.7500')