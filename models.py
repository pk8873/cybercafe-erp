from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class Operator(db.Model):
    __tablename__ = 'operators'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    shop_name = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    
    gst_number = db.Column(db.String(50))
    registration_number = db.Column(db.String(100))
    
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255))
    
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'))
    subscription_start = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_end = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    customers = db.relationship('Customer', backref='operator', lazy=True, cascade='all, delete-orphan')
    services = db.relationship('Service', backref='operator', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='operator', lazy=True, cascade='all, delete-orphan')
    complaints = db.relationship('Complaint', backref='operator', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='operator', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token
    
    def is_subscription_active(self):
        if not self.subscription_end:
            return False
        return datetime.utcnow() < self.subscription_end
    
    def get_days_remaining(self):
        if not self.subscription_end:
            return 0
        days = (self.subscription_end - datetime.utcnow()).days
        return max(0, days)
    
    def __repr__(self):
        return f'<Operator {self.shop_name}>'

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), nullable=False)
    
    full_name = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    aadhaar_last4 = db.Column(db.String(4))
    address = db.Column(db.Text)
    village = db.Column(db.String(100))
    district = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    services = db.relationship('Service', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.full_name}>'

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    service_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    payment_amount = db.Column(db.Float, nullable=False, default=0)
    
    status = db.Column(db.String(50), default='Pending')
    
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)
    
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    documents = db.relationship('Document', backref='service', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='service', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Service {self.service_type}>'

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    
    document_type = db.Column(db.String(100))
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    original_name = db.Column(db.String(255))
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Document {self.document_type}>'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False, default=0)
    payment_method = db.Column(db.String(50), default='Cash')
    transaction_id = db.Column(db.String(200))
    
    status = db.Column(db.String(50), default='Completed')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.amount}>'

class Receipt(db.Model):
    __tablename__ = 'receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    
    receipt_number = db.Column(db.String(100), unique=True, nullable=False)
    pdf_path = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Receipt {self.receipt_number}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='info')
    
    is_read = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.title}>'

class Plan(db.Model):
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    monthly_price = db.Column(db.Float, default=0)
    yearly_price = db.Column(db.Float, default=0)
    
    max_customers = db.Column(db.Integer, default=100)
    max_services = db.Column(db.Integer, default=1000)
    storage_gb = db.Column(db.Integer, default=5)
    
    features = db.Column(db.Text)
    
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Plan {self.name}>'

class Complaint(db.Model):
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('operators.id'), nullable=False)
    
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    status = db.Column(db.String(50), default='Open')
    admin_reply = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Complaint {self.subject}>'

class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminLog {self.action}>'
