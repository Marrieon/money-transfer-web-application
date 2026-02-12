from datetime import datetime, timedelta
from decimal import Decimal
from app.models import InsuranceProduct, UserInsurancePolicy, User
from app.extensions import db

def test_insurance_product_creation(client, init_database):
    """
    Test that an InsuranceProduct can be created with correct defaults and data types.
    """
    # 1. Create a new InsuranceProduct instance
    product = InsuranceProduct(
        name="Travel Health Coverage",
        description="Comprehensive health coverage for international travel.",
        coverage_amount=Decimal("10000.00"),
        premium_amount=Decimal("99.99")
    )
    
    # 2. Add and commit to the database
    db.session.add(product)
    db.session.commit()
    
    # 3. Verify the product was created
    assert product.id is not None
    
    # 4. Fetch the record and check its attributes
    retrieved_product = db.session.get(InsuranceProduct, product.id)
    assert retrieved_product is not None
    assert retrieved_product.name == "Travel Health Coverage"
    assert retrieved_product.coverage_amount == Decimal("10000.00")
    # Check the default value for 'is_active'
    assert retrieved_product.is_active is True

def test_user_insurance_policy_creation(client, init_database):
    """
    Test that a UserInsurancePolicy can be created.
    """
    # Get a user and an insurance product from the test fixture
    user = User.query.filter_by(email='user1@test.com').first()
    product = InsuranceProduct.query.filter_by(name="Device Protection").first()
    assert user is not None
    assert product is not None
    
    # Define start and end dates for the policy
    start = datetime.utcnow()
    end = start + timedelta(days=365)
    
    # 1. Create a new UserInsurancePolicy instance
    policy = UserInsurancePolicy(
        user_id=user.id,
        product_id=product.id,
        start_date=start,
        end_date=end
    )
    
    # 2. Add and commit to the database
    db.session.add(policy)
    db.session.commit()
    
    # 3. Verify the policy was created
    assert policy.id is not None
    
    # 4. Fetch the record and check its attributes
    retrieved_policy = db.session.get(UserInsurancePolicy, policy.id)
    assert retrieved_policy is not None
    assert retrieved_policy.user_id == user.id
    assert retrieved_policy.product_id == product.id
    # Check the default value for 'status'
    assert retrieved_policy.status == 'active'

def test_user_insurance_policy_relationships(client, init_database):
    """
    Test the relationships between UserInsurancePolicy, User, and InsuranceProduct.
    """
    user = User.query.filter_by(email='user1@test.com').first()
    product = InsuranceProduct.query.filter_by(name="Device Protection").first()
    
    policy = UserInsurancePolicy(
        user_id=user.id,
        product_id=product.id,
        end_date=datetime.utcnow() + timedelta(days=30)
    )
    db.session.add(policy)
    db.session.commit()
    
    # Fetch the policy and test the relationships
    retrieved_policy = db.session.get(UserInsurancePolicy, policy.id)
    
    # Test the '.user' relationship
    assert retrieved_policy.user is not None
    assert retrieved_policy.user.email == user.email
    
    # Test the '.product' relationship
    assert retrieved_policy.product is not None
    assert retrieved_policy.product.name == product.name