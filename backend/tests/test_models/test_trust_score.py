from app.models import TrustScoreRecord, User
from app.extensions import db

def test_trust_score_record_creation(client, init_database):
    """
    Test that a TrustScoreRecord can be created successfully.
    """
    # Get a user from the test fixture
    user = User.query.filter_by(email='user1@test.com').first()
    
    # 1. Create a new TrustScoreRecord instance
    record = TrustScoreRecord(
        user_id=user.id,
        score=55.5,
        reason="successful_transfer_sent"
    )
    
    # 2. Add and commit to the database
    db.session.add(record)
    db.session.commit()
    
    # 3. Verify the record was created and has an ID
    assert record.id is not None
    
    # 4. Fetch the record and check its attributes
    retrieved_record = db.session.get(TrustScoreRecord, record.id)
    assert retrieved_record is not None
    assert retrieved_record.user_id == user.id
    assert retrieved_record.score == 55.5
    assert retrieved_record.reason == "successful_transfer_sent"

def test_trust_score_user_relationship(client, init_database):
    """
    Test the relationship and back-population between TrustScoreRecord and User.
    """
    user = User.query.filter_by(email='user2@test.com').first()
    
    # Create a couple of records for the user
    record1 = TrustScoreRecord(user_id=user.id, score=50.0, reason="initial_setup")
    record2 = TrustScoreRecord(user_id=user.id, score=51.5, reason="successful_transfer_sent")
    
    db.session.add_all([record1, record2])
    db.session.commit()
    
    # 1. Test the forward relationship from the record to the user
    retrieved_record = db.session.get(TrustScoreRecord, record2.id)
    assert retrieved_record.user is not None
    assert retrieved_record.user.email == user.email
    
    # 2. Test the back-population from the user to their history
    # We must refresh the user object to load the new relationship data
    db.session.refresh(user)
    
    assert user.trust_score_history is not None
    # We expect 2 records: the one from the fixture and the two we just added.
    # Note: The conftest was updated to add an initial record.
    assert user.trust_score_history.count() == 3 
    
    # Check that one of the records in the history is the one we created
    history_reasons = {rec.reason for rec in user.trust_score_history}
    assert "successful_transfer_sent" in history_reasons