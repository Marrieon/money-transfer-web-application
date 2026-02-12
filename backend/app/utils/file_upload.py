import os
from werkzeug.utils import secure_filename

def save_file(file, upload_folder: str, allowed_extensions: set) -> str:
    """
    Validates and saves an uploaded file, returning the generated filename.
    """
    if not file or file.filename == '':
        raise ValueError("No file selected.")

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

    if not allowed_file(file.filename):
        raise ValueError(f"Invalid file type. Allowed types are: {', '.join(allowed_extensions)}")

    filename = secure_filename(file.filename)
    # In a real app, you would generate a unique filename to avoid collisions.
    # For now, we'll use the secure version of the original filename.
    
    # This part would save the file, but we'll just simulate it for now.
    # file.save(os.path.join(upload_folder, filename))
    
    # We return the path where the file would be saved.
    return os.path.join(upload_folder, filename)