from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import string

db = SQLAlchemy()

class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.String(13), unique=True, nullable=False) # The 13-digit ID
    shop_name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20), unique=True)
    address = db.Column(db.Text)
    dob = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PrintJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pickup_code = db.Column(db.String(4), unique=True, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    is_color = db.Column(db.Boolean, default=False)
    copies = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='pending') # pending, printed, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super(PrintJob, self).__init__(**kwargs)
        # Generate a unique 4-digit code
        self.pickup_code = self.generate_unique_code()
        # Set expiration to 30 minutes from now
        self.expires_at = datetime.utcnow() + timedelta(minutes=30)

    def generate_unique_code(self):
        """Generates a code like '5829' and ensures it isn't already in use."""
        while True:
            code = ''.join(random.choices(string.digits, k=4))
            if not PrintJob.query.filter_by(pickup_code=code).first():
                return code