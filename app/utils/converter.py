import subprocess
import os
from PIL import Image  # Add this import
import platform # Add this to detect Windows vs Linux

def convert_to_pdf(input_filename, upload_folder):
    input_path = os.path.abspath(os.path.join(upload_folder, input_filename))
    file_basename = os.path.splitext(input_filename)[0]
    output_pdf_name = f"{file_basename}.pdf"
    
    # 1. Detect OS and set the correct LibreOffice Command
    if platform.system() == "Windows":
        # CHANGE THIS PATH if yours is different!
        libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'
    else:
        libreoffice_path = 'libreoffice'

    # 2. Run the conversion
    try:
        process = subprocess.run([
            libreoffice_path, 
            '--headless', 
            '--convert-to', 'pdf', 
            '--outdir', upload_folder, 
            input_path
        ], capture_output=True, text=True, timeout=60)

        if process.returncode == 0:
            if os.path.exists(input_path):
                os.remove(input_path)
            return output_pdf_name
        else:
            print(f"LibreOffice Error: {process.stderr}")
            return None
            
    except Exception as e:
        print(f"System Error: {e}")
        return None