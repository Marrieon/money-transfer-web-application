import pytest
from app import create_app
from app.extensions import db
# Import all models needed for test data setup across all phases
from app.models import User, Wallet, InsuranceProduct, TrustScoreRecord

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app('testing')
    return app

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app. This runs for each test function."""
    with app.test_client() as client:
        with app.app_context():
            # Create all database tables before the test runs
            db.create_all()
            yield client
            # Clean up the database after the test runs
            db.session.remove()
            db.drop_all()

@pytest.fixture(scope='function')
def init_database(client):
    """
    Set up the database with a standard set of users and data for tests.
    This fixture ensures a consistent starting point for most tests.
    """
    # === Create Users ===
    admin_user = User(
        email='admin@test.com', phone='0000000000', 
        first_name='Admin', last_name='User', is_admin=True
    )
    admin_user.set_password('adminpass')
    
    # This user will have a default trust score of 50
    user1 = User(
        email='user1@test.com', phone='1111111111',
        first_name='Test', last_name='User1'
    )
    user1.set_password('user1pass')
    
    # This user will also have a default trust score of 50
    user2 = User(
        email='user2@test.com', phone='2222222222',
        first_name='Test', last_name='User2'
    )
    user2.set_password('user2pass')
    
    db.session.add_all([admin_user, user1, user2])
    db.session.commit()

    # === Create Wallets ===
    wallet_admin = Wallet(user_id=admin_user.id, balance=1000)
    wallet1 = Wallet(user_id=user1.id, balance=100)
    wallet2 = Wallet(user_id=user2.id, balance=50)
    
    db.session.add_all([wallet_admin, wallet1, wallet2])
    db.session.commit()
    
    # === Create Initial Trust Score Records (CORRECTED) ===
    # This is crucial for tests that rely on a starting trust score.
    # We create a baseline record for each user to match the default score in the model.
    ts_record_admin = TrustScoreRecord(user_id=admin_user.id, score=admin_user.trust_score, reason="initial_setup")
    ts_record1 = TrustScoreRecord(user_id=user1.id, score=user1.trust_score, reason="initial_setup")
    ts_record2 = TrustScoreRecord(user_id=user2.id, score=user2.trust_score, reason="initial_setup")

    db.session.add_all([ts_record_admin, ts_record1, ts_record2])
    db.session.commit()

    # === Create Other Test Data (e.g., for Phase 4) ===
    insurance_product = InsuranceProduct(
        name="Device Protection",
        description="One year protection for your mobile device.",
        coverage_amount=500,
        premium_amount=25.00
    )
    db.session.add(insurance_product)
    db.session.commit()