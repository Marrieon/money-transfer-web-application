import json
from decimal import Decimal
from app.models import Merchant, Wallet

def test_create_merchant_account(client, init_database):
    """Test a user successfully creating a merchant account."""
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    res = client.post('/api/merchants/account', headers=headers, json={
        "business_name": "Newton's Gadgets"
    })
    assert res.status_code == 201
    assert "Merchant account created" in res.get_json()['message']
    assert "api_key" in res.get_json()

    merchant = Merchant.query.filter_by(user_id=2).first() # User1's ID
    assert merchant is not None
    assert merchant.business_name == "Newton's Gadgets"

def test_get_merchant_account(client, init_database):
    """Test retrieving merchant account details."""
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Create account first
    client.post('/api/merchants/account', headers=headers, json={"business_name": "Test Shop"})
    
    # Get details
    res = client.get('/api/merchants/account', headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data['business_name'] == "Test Shop"
    assert "api_key" in data

def test_merchant_payment_success(client, init_database):
    """Test a successful payment from a customer to a merchant."""
    # User1 becomes a merchant
    login_res_merchant = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token_merchant = login_res_merchant.get_json()['access_token']
    headers_merchant = {'Authorization': f'Bearer {token_merchant}'}
    create_res = client.post('/api/merchants/account', headers=headers_merchant, json={"business_name": "Test Shop"})
    api_key = create_res.get_json()['api_key']

    # User2 (customer) pays User1 (merchant)
    payment_headers = {'X-API-KEY': api_key}
    res = client.post('/api/merchants/pay', headers=payment_headers, json={
        "customer_phone": "2222222222", # User2's phone
        "amount": "15.00"
    })
    
    assert res.status_code == 200
    assert "Payment successful" in res.get_json()['message']

    # Verify wallet balances
    # Fee for $15 is 15 * 0.005 = 0.075. Total debit = 15.075
    wallet_customer = Wallet.query.filter_by(user_id=3).first() # User2's wallet
    wallet_merchant = Wallet.query.filter_by(user_id=2).first() # User1's wallet
    assert wallet_customer.balance == Decimal('50.0000') - Decimal('15.0750')
    assert wallet_merchant.balance == Decimal('100.0000') + Decimal('15.0000')