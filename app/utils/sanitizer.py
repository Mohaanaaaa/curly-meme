import os
import uuid
from werkzeug.utils import secure_filename

# Define allowed formats based on your requirements
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'txt'}

def is_allowed(filename):
    """Check if the file extension is in the allowed list."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_safe_name(original_filename):
    """
    Creates a completely random filename to prevent 
    directory traversal attacks and hide original metadata.
    """
    ext = original_filename.rsplit('.', 1)[1].lower()
    random_name = f"{uuid.uuid4().hex}.{ext}"
    return random_name

def save_file_safely(file_object, upload_folder):
    """
    The main workflow: Check -> Rename -> Save
    """
    if not file_object or not is_allowed(file_object.filename):
        return None, "Invalid file type."

    # 1. Clean the original name (standard security)
    original_name = secure_filename(file_object.filename)
    
    # 2. Generate our random internal name
    safe_name = generate_safe_name(original_name)
    
    # 3. Create the full path
    filepath = os.path.join(upload_folder, safe_name)
    
    # 4. Save to disk
    file_object.save(filepath)
    
    return safe_name, None