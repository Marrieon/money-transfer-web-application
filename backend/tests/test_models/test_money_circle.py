from decimal import Decimal
from app.models import MoneyCircle, User
from app.extensions import db

def test_money_circle_creation(client, init_database):
    """
    Test that a MoneyCircle record can be created with its default frequency.
    """
    # Get a user from the fixture to act as the creator
    creator_user = User.query.filter_by(email='user1@test.com').first()
    
    # 1. Create a new MoneyCircle instance
    circle = MoneyCircle(
        name="Weekly Savings Group",
        description="A group for saving weekly.",
        contribution_amount=Decimal("25.00"),
        frequency=7, # Override the default
        created_by_user_id=creator_user.id
    )
    
    # 2. Add and commit to the database
    db.session.add(circle)
    db.session.commit()
    
    # 3. Verify the record was created and has an ID
    assert circle.id is not None
    
    # 4. Fetch the record and check its attributes
    retrieved_circle = db.session.get(MoneyCircle, circle.id)
    assert retrieved_circle is not None
    assert retrieved_circle.name == "Weekly Savings Group"
    assert retrieved_circle.frequency == 7
    
    # Test creation with default frequency
    default_circle = MoneyCircle(
        name="Monthly Circle",
        contribution_amount=Decimal("100.00"),
        created_by_user_id=creator_user.id
    )
    db.session.add(default_circle)
    db.session.commit()
    assert default_circle.frequency == 30

def test_money_circle_creator_relationship(client, init_database):
    """
    Test that the one-to-many 'creator' relationship is correctly linked.
    """
    creator_user = User.query.filter_by(email='user1@test.com').first()
    
    circle = MoneyCircle(
        name="Creator's Circle",
        contribution_amount=Decimal("50.00"),
        created_by_user_id=creator_user.id
    )
    db.session.add(circle)
    db.session.commit()
    
    # Fetch the circle and test the relationship
    retrieved_circle = db.session.get(MoneyCircle, circle.id)
    assert retrieved_circle.creator is not None
    assert retrieved_circle.creator.email == creator_user.email

def test_money_circle_members_many_to_many_relationship(client, init_database):
    """
    Test the many-to-many 'members' relationship.
    """
    creator_user = User.query.filter_by(email='user1@test.com').first()
    member_user = User.query.filter_by(email='user2@test.com').first()
    
    # 1. Create a circle
    circle = MoneyCircle(
        name="Community Pool",
        contribution_amount=Decimal("10.00"),
        created_by_user_id=creator_user.id
    )
    
    # 2. Add members to the circle
    circle.members.append(creator_user)
    circle.members.append(member_user)
    
    db.session.add(circle)
    db.session.commit()
    
    # 3. Fetch the circle and verify the members
    retrieved_circle = db.session.get(MoneyCircle, circle.id)
    assert retrieved_circle is not None
    assert len(retrieved_circle.members) == 2
    # Check that both users are in the members list
    member_emails = {member.email for member in retrieved_circle.members}
    assert creator_user.email in member_emails
    assert member_user.email in member_emails
    
    # 4. Verify the relationship from the User side (the backref)
    retrieved_creator = db.session.get(User, creator_user.id)
    retrieved_member = db.session.get(User, member_user.id)
    assert len(retrieved_creator.money_circles) == 1
    assert len(retrieved_member.money_circles) == 1
    assert retrieved_creator.money_circles[0].name == "Community Pool"