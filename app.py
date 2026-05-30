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
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import models AFTER db is created
from models import Operator, Customer, Service, Payment, Notification, Plan, Complaint, AdminLog, Document, Receipt

# Import blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.customer import customer_bp
from routes.service import service_bp
from routes.admin import admin_bp
from routes.pdf_tools import pdf_tools_bp
from routes.reports import reports_bp
from routes.api import api_bp

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
    logger.error(f'404 Error: {error}')
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    try:
        db.session.rollback()
    except:
        pass
    logger.error(f'500 Server Error: {str(error)}', exc_info=True)
    return render_template('errors/500.html', error=str(error)), 500

@app.errorhandler(403)
def forbidden(error):
    logger.error(f'403 Forbidden: {error}')
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
    try:
        plans = Plan.query.filter_by(active=True).all()
        return render_template('pricing.html', plans=plans)
    except Exception as e:
        logger.error(f'Pricing page error: {e}')
        return render_template('pricing.html', plans=[])

# Contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            phone = request.form.get('phone')
            
            logger.info(f'Contact: {name} ({email}) - {message}')
            flash('आपका संदेश भेज दिया गया। धन्यवाद!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            logger.error(f'Contact form error: {e}')
            flash('संदेश भेजने में त्रुटि।', 'error')
    
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

# Health check
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info('Database tables created/verified')
        except Exception as e:
            logger.error(f'Database creation error: {e}')
    
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
