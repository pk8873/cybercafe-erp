import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import secrets
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://arcade_hub_db_005a_user:1eFI2CcvxvhXrdzMiTh8y9Ap2l8jdhIo@dpg-d876pqt7vvec738o5r10-a/arcade_hub_db_005a')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import models
from models import Operator, Customer, Service, Payment, Notification, Plan, Complaint, AdminLog, Document, Receipt

# Import blueprints
from routes import auth_bp, dashboard_bp, customer_bp, service_bp, admin_bp, pdf_tools_bp, reports_bp, api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(service_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(pdf_tools_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(api_bp)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    db.session.rollback()
    logger.error(f'Server error: {error}')
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Pricing page
@app.route('/pricing')
def pricing():
    plans = Plan.query.filter_by(active=True).all()
    return render_template('pricing.html', plans=plans)

# Contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        phone = request.form.get('phone')
        
        # Log contact message (can be extended to email notification)
        logger.info(f'Contact: {name} ({email}) - {message}')
        flash('आपका संदेश भेज दिया गया। धन्यवाद!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# FAQ page
@app.route('/faq')
def faq():
    return render_template('faq.html')

# Terms page
@app.route('/terms')
def terms():
    return render_template('terms.html')

# Privacy page
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# Health check for deployment
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
