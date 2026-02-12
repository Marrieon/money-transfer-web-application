import pytest
from unittest.mock import MagicMock
from app.utils.file_upload import save_file

def test_save_file_success():
    """Test a successful (simulated) file save."""
    # Create a mock file object that behaves like a FileStorage object
    mock_file = MagicMock()
    mock_file.filename = 'profile_picture.jpg'
    
    allowed_extensions = {'jpg', 'png'}
    upload_folder = '/static/uploads'
    
    result_path = save_file(mock_file, upload_folder, allowed_extensions)
    
    assert result_path == '/static/uploads/profile_picture.jpg'

def test_save_file_invalid_extension():
    """Test that saving a file with a disallowed extension raises an error."""
    mock_file = MagicMock()
    mock_file.filename = 'document.pdf'
    
    allowed_extensions = {'jpg', 'png'}
    upload_folder = '/static/uploads'
    
    with pytest.raises(ValueError, match="Invalid file type"):
        save_file(mock_file, upload_folder, allowed_extensions)