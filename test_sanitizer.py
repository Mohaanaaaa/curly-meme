from app.utils.sanitizer import generate_safe_name, is_allowed

test_file = "my_private_resume_2024.docx"

if is_allowed(test_file):
    print(f"File Allowed: {test_file}")
    safe_name = generate_safe_name(test_file)
    print(f"Stored as: {safe_name}")
else:
    print("Blocked!")