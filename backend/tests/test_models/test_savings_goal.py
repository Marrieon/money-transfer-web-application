from datetime import date, timedelta
from decimal import Decimal
from app.models import SavingsGoal, User
from app.extensions import db

def test_savings_goal_creation(client, init_database):
    """
    Test that a SavingsGoal record can be created with its default 'current_amount'.
    """
    # Get a user from the fixture to own the savings goal
    user = User.query.filter_by(email='user1@test.com').first()
    
    # 1. Create a new SavingsGoal instance
    goal = SavingsGoal(
        user_id=user.id,
        title="Vacation to Hawaii",
        target_amount=Decimal("3000.00"),
        deadline=date.today() + timedelta(days=180)
    )
    
    # 2. Add and commit to the database
    db.session.add(goal)
    db.session.commit()
    
    # 3. Verify the record was created and has an ID
    assert goal.id is not None
    
    # 4. Fetch the record and check its attributes
    retrieved_goal = db.session.get(SavingsGoal, goal.id)
    assert retrieved_goal is not None
    assert retrieved_goal.title == "Vacation to Hawaii"
    assert retrieved_goal.target_amount == Decimal("3000.0000")
    assert retrieved_goal.deadline is not None
    
    # Check the default value for 'current_amount'
    assert retrieved_goal.current_amount == Decimal("0.0000")

def test_savings_goal_nullable_deadline(client, init_database):
    """
    Test that a SavingsGoal can be created without a deadline.
    """
    user = User.query.filter_by(email='user1@test.com').first()
    
    goal_no_deadline = SavingsGoal(
        user_id=user.id,
        title="Emergency Fund",
        target_amount=Decimal("1000.00"),
        deadline=None # Explicitly set to None
    )
    db.session.add(goal_no_deadline)
    db.session.commit()
    
    retrieved_goal = db.session.get(SavingsGoal, goal_no_deadline.id)
    assert retrieved_goal is not None
    assert retrieved_goal.deadline is None

def test_savings_goal_user_relationship(client, init_database):
    """
    Test that the 'user' relationship is correctly linked.
    """
    user = User.query.filter_by(email='user2@test.com').first()
    
    goal = SavingsGoal(
        user_id=user.id,
        title="New Laptop",
        target_amount=Decimal("1500.00")
    )
    db.session.add(goal)
    db.session.commit()
    
    # Fetch the goal and test the relationship
    retrieved_goal = db.session.get(SavingsGoal, goal.id)
    
    assert retrieved_goal.user is not None
    assert retrieved_goal.user.email == user.email