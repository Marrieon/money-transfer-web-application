import json
# CORRECTED: This import was in the wrong place.
from app.services import backup_service

def test_create_database_backup(client, init_database):
    """Test that the backup service can pull data and format it correctly."""
    
    # The call to the service function belongs INSIDE the test function.
    backup_result = backup_service.create_database_backup()
    
    # Check that a filename was generated
    assert "filename" in backup_result
    assert backup_result["filename"].startswith("backup_")
    assert backup_result["filename"].endswith(".json")
    
    # Check that the data contains our test users
    data = json.loads(backup_result["data"])
    assert isinstance(data, list)
    # We created 3 users in the init_database fixture
    assert len(data) == 3 
    
    # Check that the data for one of the users is correct
    user1_data = next((item for item in data if item["email"] == "user1@test.com"), None)
    assert user1_data is not None
    assert user1_data["phone"] == "1111111111"
