import json
from decimal import Decimal
from app.models import Wallet, UserInsurancePolicy

def test_get_insurance_products(client, init_database):
    """Test that anyone can see the list of active insurance products."""
    res = client.get('/api/insurance/products')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['name'] == 'Device Protection'
    assert data[0]['premium_amount'] == 25.0

def test_admin_can_create_product(client, init_database):
    """Test that an admin user can create a new insurance product."""
    login_res = client.post('/api/auth/login', json={'email': 'admin@test.com', 'password': 'adminpass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    res = client.post('/api/insurance/products', headers=headers, json={
        "name": "Travel Insurance",
        "description": "Coverage for your next trip.",
        "coverage_amount": 2000,
        "premium_amount": 75.50
    })
    assert res.status_code == 201
    assert "Insurance product created" in res.get_json()['message']

def test_user_can_purchase_insurance(client, init_database):
    """Test a regular user successfully purchasing an insurance policy."""
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Product ID 1 was created by the conftest fixture
    res = client.post('/api/insurance/purchase/1', headers=headers)
    assert res.status_code == 201
    assert "Policy purchased successfully" in res.get_json()['message']

    # Verify user's wallet was debited
    wallet = Wallet.query.filter_by(user_id=2).first() # user1's wallet
    assert wallet.balance == Decimal('100.0000') - Decimal('25.0000')

    # Verify a policy was created
    policy = UserInsurancePolicy.query.filter_by(user_id=2).first()
    assert policy is not None
    assert policy.product_id == 1

def test_purchase_insurance_insufficient_funds(client, init_database):
    """Test that a user with insufficient funds cannot purchase a policy."""
    # User2 only has $50 balance, product costs $25, so let's test a more expensive product
    # We must log in as admin to create one
    admin_login_res = client.post('/api/auth/login', json={'email': 'admin@test.com', 'password': 'adminpass'})
    admin_token = admin_login_res.get_json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    client.post('/api/insurance/products', headers=admin_headers, json={
        "name": "Life Insurance", "description": "Full life coverage",
        "coverage_amount": 100000, "premium_amount": 150
    })

    # User2 logs in
    login_res = client.post('/api/auth/login', json={'email': 'user2@test.com', 'password': 'user2pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # User2 tries to buy the expensive product (ID 2)
    res = client.post('/api/insurance/purchase/2', headers=headers)
    assert res.status_code == 400
    assert "Insufficient funds" in res.get_json()['message']