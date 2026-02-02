import os, threading, uuid, random, time, csv
from datetime import datetime, timezone, timedelta, date
from flask import Flask, request, render_template, redirect, url_for, jsonify, send_file, abort
from app.models import db, PrintJob
from app.utils.sanitizer import save_file_safely
from app.utils.converter import convert_to_pdf
from config import Config

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../print_service.db'
db.init_app(app)

with app.app_context():
    db.create_all()

def log_to_excel(event, shop, status, filename="", detail=""):
    path = 'print_shop_logs.csv'
    file_exists = os.path.isfile(path)
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Event', 'Shop', 'Status', 'File Name', 'Detail'])
        writer.writerow([
            datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), 
            event, shop, status, filename, detail
        ])
        
@app.route('/')
def index(): return render_template('customer/upload.html')

@app.route('/upload', methods=['POST'])
def handle_upload():
    file = request.files.get('file')
    if not file: return "No file", 400
    safe_name, err = save_file_safely(file, app.config['UPLOAD_FOLDER'])
    pdf = convert_to_pdf(safe_name, app.config['UPLOAD_FOLDER'])
    new_job = PrintJob(file_path=pdf, is_color=request.form.get('color')=='true', copies=int(request.form.get('copies', 1)))
    db.session.add(new_job); db.session.commit()
    return render_template('customer/ticket.html', code=new_job.pickup_code)

# --- OPTIMIZED UPLOAD (SMART DROP) ---
@app.route('/drop/<shop_id>', methods=['POST'])
def smart_drop(shop_id):
    file = request.files.get('file')
    if file and file.filename != '':
        fname = f"{uuid.uuid4().hex}_{file.filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        
        new_job = PrintJob(
            file_path=fname, 
            is_color=request.form.get('color') == 'color', 
            copies=int(request.form.get('copies', 1))
        )
        db.session.add(new_job)
        db.session.commit() 
        
        log_to_excel("SMART_DROP", shop_id, "SUCCESS", file.filename, f"Code: {new_job.pickup_code}")
        return render_template('customer/ticket.html', code=new_job.pickup_code)
    return "No file", 400

@app.route('/shop/home')
def shop_home():
    # Page to check total print counts and download reports
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    total_today = PrintJob.query.filter(PrintJob.created_at >= today).count()
    return render_template('shop/home.html', total_count=total_today)

@app.route('/shop')
def shop_dashboard():
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    total = PrintJob.query.filter(PrintJob.created_at >= today).count()
    jobs = PrintJob.query.filter_by(status='pending').order_by(PrintJob.created_at.desc()).all()
    
    # Pre-calculate values to avoid Jinja UndefinedError
    now = datetime.now(timezone.utc)
    for j in jobs:
        expiry = j.expires_at.replace(tzinfo=timezone.utc)
        j.minutes_left = max(0, int((expiry - now).total_seconds() / 60))
        j.extension = os.path.splitext(j.file_path)[1].replace('.', '').upper()
        
    return render_template('shop/dashboard.html', jobs=jobs, total_count=total)

@app.route('/api/active-jobs')
def get_active_jobs():
    jobs = PrintJob.query.filter_by(status='pending').order_by(PrintJob.created_at.desc()).all()
    now = datetime.now(timezone.utc)
    return jsonify([{
        "code": j.pickup_code, 
        "is_color": "Color" if j.is_color else "B&W",
        "copies": j.copies, 
        "file_path": j.file_path,
        "time_left": f"{max(0, int((j.expires_at.replace(tzinfo=timezone.utc)-now).total_seconds()/60))}m"
    } for j in jobs])

# Ensure the download route prevents auto-downloads
@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        abort(404)
    # as_attachment=False is CRITICAL for direct browser printing
    return send_file(file_path, as_attachment=False)

def start_cleanup_daemon(app):
    def cleanup():
        with app.app_context():
            while True:
                limit = datetime.now(timezone.utc) - timedelta(minutes=10)
                expired = PrintJob.query.filter(PrintJob.created_at <= limit).all()
                for job in expired:
                    try:
                        p = os.path.join(app.config['UPLOAD_FOLDER'], job.file_path)
                        if os.path.exists(p): os.remove(p)
                        db.session.delete(job); db.session.commit()
                    except: pass
                time.sleep(300)
    threading.Thread(target=cleanup, daemon=True).start()

if __name__ == '__main__':
    start_cleanup_daemon(app); app.run(debug=True)