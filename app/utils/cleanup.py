import os
from datetime import datetime
from app.models import db, PrintJob

def purge_expired_files(upload_folder):
    # Find jobs where current time is past expiration
    expired_jobs = PrintJob.query.filter(PrintJob.expires_at <= datetime.utcnow()).all()
    
    for job in expired_jobs:
        file_path = os.path.join(upload_folder, job.file_path)
        # 1. Delete the physical file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 2. Remove record from database
        db.session.delete(job)
    
    db.session.commit()