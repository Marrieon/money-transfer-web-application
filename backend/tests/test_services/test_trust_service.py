from app.services.trust_service import update_trust_score
from app.models import User, TrustScoreRecord

def test_update_trust_score(client, init_database):
    """Test the basic trust score update functionality."""
    user = User.query.filter_by(email='user1@test.com').first()
    initial_score = user.trust_score

    # Give user positive points
    new_score = update_trust_score(user.id, "test_reason_positive", 10.5)
    
    assert new_score == initial_score + 10.5
    assert user.trust_score == initial_score + 10.5
    
    # Check that a record was created
    record = TrustScoreRecord.query.filter_by(user_id=user.id).order_by(TrustScoreRecord.id.desc()).first()
    assert record is not None
    assert record.reason == "test_reason_positive"
    assert record.score == new_score