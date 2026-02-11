import os, threading, uuid, random, time, csv
from datetime import datetime, timezone, timedelta, date
from flask import Flask, request, render_template, redirect, url_for, jsonify, send_file, abort,flash, session
from app.models import db, PrintJob , Shop
from app.utils.sanitizer import save_file_safely
from app.utils.converter import convert_to_pdf
from config import Config
import hashlib

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../print_service.db'

# --- CRITICAL FIXES ---
# Added secret_key to fix white screen and session errors
app.secret_key = 'station_secure_key_13_digits'
app.config['SESSION_PERMANENT'] = False
app.config['USE_SESSION_COOKIES'] = True

db.init_app(app)

with app.app_context():
    db.create_all()

def log_to_excel(event, shop, status, filename="", detail=""):
    path = 'print_shop_logs.csv'
    file_exists = os.path.isfile(path)
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f)
        # Added 'File Name' column for professional auditing
        if not file_exists:
            writer.writerow(['Timestamp', 'Event', 'Shop', 'Status', 'File Name', 'Detail'])
        writer.writerow([
            datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), 
            event, shop, status, filename, detail
        ])
        
'''@app.route('/')
def index(): return render_template('customer/upload.html')
'''
@app.route('/')
def index(): 
    # Default behavior for generic visits
    return render_template('customer/upload.html', shop_id=None)

@app.route('/upload', methods=['POST'])
def handle_upload():
    file = request.files.get('file')
    if not file: return "No file", 400
    safe_name, err = save_file_safely(file, app.config['UPLOAD_FOLDER'])
    pdf = convert_to_pdf(safe_name, app.config['UPLOAD_FOLDER'])
    new_job = PrintJob(file_path=pdf, is_color=request.form.get('color')=='true', copies=int(request.form.get('copies', 1)))
    db.session.add(new_job); db.session.commit()
    return render_template('customer/ticket.html', code=new_job.pickup_code)


# 1. This tracks scan timing to block replicas
recent_scans = {}

# Mock function for generating 13-digit ID
# Helper function to generate the 13-digit numeric ID
def generate_station_id(phone):
    # Combine phone and current time for a unique seed
    seed = f"{phone}{time.time()}"
    # Create a numeric hash
    numeric_hash = str(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    # Return exactly 13 digits
    return numeric_hash[:13]


'''@app.route('/shop/register', methods=['GET','POST'])
def handle_registration():
    if request.method == 'GET':
        return render_template('shop/registration.html')
    try:
        # 1. Capture Form Data
        shop_name = request.form.get('shop_name')
        owner_name = request.form.get('owner_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        dob = request.form.get('dob')
        captcha_input = request.form.get('captcha_input')  # The code user typed

        # 2. Security Check: Validate Agreement
        if not request.form.get('agreement'):
            return jsonify({"status": "error", "message": "You must accept the terms"}), 400

        # 3. Security Check: CAPTCHA (Simplified example)
        # In a real app, you'd compare this against a session-stored value
        if captcha_input != "X8R2Q":
            return jsonify({"status": "error", "message": "Invalid CAPTCHA"}), 400

        # 4. Generate the Unique 13-digit Shop ID
        new_shop_id = generate_station_id(phone)

        # 5. Save to Database (uncomment and implement accordingly)
        new_shop = Shop(
             shop_id=new_shop_id,
             shop_name=shop_name,
             owner_name=owner_name,
             email=email,
             phone=phone,
             address=address,
             dob=dob
         )
        db.session.add(new_shop)
        db.session.commit()

        # 6. Success Response
        return render_template('shop/registration_success.html', 
                               shop_id=new_shop_id, 
                               shop_name=shop_name)

    except Exception as e:
        print(f"Registration Error: {e}")
        # In case of error, respond with error message
        return jsonify({
            "status": "error",
            "message": "Registration failed due to an internal error."
        }), 500'''
        
# FIXED: Added 'GET' to allow viewing the form. Original was POST-only
@app.route('/shop/register', methods=['GET', 'POST'])
def handle_registration():
    if request.method == 'POST':
        try:
            # Fetch form data
            shop_name = request.form.get('shop_name')
            owner_name = request.form.get('owner_name')  # added
            email = request.form.get('email')            # added
            phone = request.form.get('phone')
            address = request.form.get('address')        # added
            dob = request.form.get('dob')                 # added

            if not request.form.get('agreement'):
                return jsonify({"status": "error", "message": "You must accept the terms"}), 400

            new_shop_id = generate_station_id(phone)

            # Save to Database
            new_shop = Shop(
                shop_id=new_shop_id,
                shop_name=shop_name,
                owner_name=owner_name,
                email=email,
                phone=phone,
                address=address,
                dob=dob
            )
            db.session.add(new_shop)
            db.session.commit()

            # Render success page
            return render_template('shop/registration_success.html', 
                                   shop_id=new_shop_id, 
                                   shop_name=shop_name)
        except Exception as e:
            db.session.rollback()  # rollback in case of error
            return jsonify({"status": "error", "message": str(e)}), 500

    # Render registration form for GET requests
    return render_template('shop/register.html')

@app.route('/drop/<string:shop_id>', methods=['GET'])
def shop_direct_link(shop_id):
    # If the URL is exactly 13 digits, we know it's a Shop QR visit
    is_locked = len(shop_id) == 13
    return render_template('customer/upload.html', shop_id=shop_id, locked=is_locked)

@app.route('/shop/login', methods=['GET', 'POST'])
def shop_login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        station_id = request.form.get('station_id')
        
        # This now works because Shop is imported
        shop = Shop.query.filter_by(shop_id=station_id, phone=phone).first()
        
        if shop:
            session.permanent = False
            session['shop_id'] = shop.shop_id
            session['shop_name'] = shop.shop_name
            return redirect(url_for('shop_home'))
        else:
            flash("Invalid Phone or Station ID")
            
    return render_template('shop/login.html')

@app.route('/debug/shops')
def debug_shops():
    # Fetch all registered shops from the DB
    shops = Shop.query.all()
    return jsonify([{
        "name": s.shop_name, 
        "id": s.shop_id, 
        "phone": s.phone
    } for s in shops])

@app.route('/drop/<shop_id>', methods=['POST'])
def smart_drop(shop_id):
    file = request.files.get('file')
    if file and file.filename != '':
        current_time = time.time()
        scan_key = f"{shop_id}_{file.filename}"
        
        # --- DUPLICATE LOCK WITH REAL TOKEN ---
        if scan_key in recent_scans:
            last_time, saved_code = recent_scans[scan_key]
            # If same file within 10 seconds, show the PREVIOUS token
            if current_time - last_time < 10:
                return render_template('customer/ticket.html', code=saved_code)
        
        # Save unique file
        fname = f"{uuid.uuid4().hex}_{file.filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        
        # Create Job
        new_job = PrintJob(
            file_path=fname, 
            is_color=request.form.get('color') == 'color', 
            copies=int(request.form.get('copies', 1))
        )
        db.session.add(new_job)
        db.session.commit() 
        
        # Save this specific token to our "Duplicate Lock"
        recent_scans[scan_key] = (current_time, new_job.pickup_code)
        
        log_to_excel("SMART_DROP", shop_id, "SUCCESS", file.filename, f"Code: {new_job.pickup_code}")
        
        return render_template('customer/ticket.html', code=new_job.pickup_code)
    return "No file", 400

'''@app.route('/shop/home')
def shop_home():
    if 'shop_id' not in session:
        return redirect(url_for('shop_login'))
    # Page to check total print counts and download reports
    #today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    # Filter jobs only for this specific shop's 13-digit ID
    total_count = PrintJob.query.filter_by(shop_id=session['shop_id']).count()
    return render_template('shop/home.html', total_count=total_count)'''
    
@app.route('/shop/home')
def shop_home():
    # Session check prevents 'NameError: session is not defined'
    if 'shop_id' not in session:
        return redirect(url_for('shop_login')) # Fixed for BuildError
        
    total_count = PrintJob.query.count() # Passed to home.html
    return render_template('shop/home.html', total_count=total_count)

@app.route('/shop')
def shop_dashboard():
    # ... previous logic ...
    jobs = PrintJob.query.filter_by(status='pending').order_by(PrintJob.created_at.desc()).all()
    now = datetime.now(timezone.utc)
    for j in jobs:
        # FIXED: This ensures the scan format (PDF/JPG) shows correctly on terminal
        file_ext = os.path.splitext(j.file_path)[1].replace('.', '').upper()
        j.extension = file_ext if file_ext else "SCAN"
        
        expiry = j.expires_at.replace(tzinfo=timezone.utc)
        j.minutes_left = max(0, int((expiry - now).total_seconds() / 60))
    return render_template('shop/dashboard.html', jobs=jobs)
    
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
    
@app.route('/shop/logout')
def logout():
    session.clear() # Deletes all data from the current session
    return redirect(url_for('shop_login'))

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        abort(404)
    # Allows the terminal to print directly
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