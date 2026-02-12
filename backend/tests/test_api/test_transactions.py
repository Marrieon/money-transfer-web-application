import json
from decimal import Decimal
from app.models import Wallet

def test_get_transaction_history(client, init_database):
    # First, log in user1 to get a token
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Make a test transaction
    client.post('/api/transactions/transfer', headers=headers, json={
        'receiver_phone': '2222222222',
        'amount': '10.50'
    })

    # Now get history
    res = client.get('/api/transactions/history', headers=headers)
    assert res.status_code == 200
    history = res.get_json()
    assert len(history) == 1
    assert history[0]['type'] == 'sent'
    assert history[0]['amount'] == 10.50

def test_successful_transfer(client, init_database):
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    res = client.post('/api/transactions/transfer', headers=headers, json={
        'receiver_phone': '2222222222',
        'amount': '25.00'
    })
    
    assert res.status_code == 201
    assert res.get_json()['message'] == 'Transfer successful'

    # Verify wallet balances
    wallet1 = Wallet.query.filter_by(user_id=2).first() # user1
    wallet2 = Wallet.query.filter_by(user_id=3).first() # user2

    # Fee is 0.5% of 25 = 0.125. Total debit = 25.125
    # Sender's initial balance is 100. New balance is 100 - 25.125 = 74.875
    # Receiver's initial balance is 50. New balance is 50 + 25 = 75
    
    # MODIFIED: Asserting against the exact Decimal value now that precision is fixed
    assert wallet1.balance == Decimal('74.8750')
    assert wallet2.balance == Decimal('75.0000')

def test_insufficient_funds_transfer(client, init_database):
    login_res = client.post('/api/auth/login', json={'email': 'user1@test.com', 'password': 'user1pass'})
    token = login_res.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    res = client.post('/api/transactions/transfer', headers=headers, json={
        'receiver_phone': '2222222222',
        'amount': '200.00' # user1 only has 100
    })
    
    assert res.status_code == 400
    assert res.get_json()['message'] == 'Insufficient funds.'