from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
from app import db
from models import Operator, Plan
import secrets
import re

auth_bp = Blueprint('auth', __name__, url_prefix='')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'operator_id' not in session:
            flash('कृपया पहले लॉगिन करें', 'error')
            return redirect(url_for('auth.login'))
        
        operator = Operator.query.get(session['operator_id'])
        if not operator or not operator.is_active:
            session.clear()
            flash('खाता निष्क्रिय है', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required', 'error')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        shop_name = request.form.get('shop_name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        district = request.form.get('district', '').strip()
        address = request.form.get('address', '').strip()
        
        # Validation
        if not all([full_name, shop_name, mobile, email, password, district]):
            flash('सभी आवश्यक फील्ड भरें', 'error')
            return redirect(url_for('auth.register'))
        
        if len(password) < 8:
            flash('पासवर्ड कम से कम 8 वर्णों का होना चाहिए', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('पासवर्ड मेल नहीं खाते', 'error')
            return redirect(url_for('auth.register'))
        
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash('वैध ईमेल दर्ज करें', 'error')
            return redirect(url_for('auth.register'))
        
        if not re.match(r'^\d{10}$', mobile):
            flash('वैध 10 अंकों का मोबाइल नंबर दर्ज करें', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if operator exists
        if Operator.query.filter_by(email=email).first():
            flash('यह ईमेल पहले से पंजीकृत है', 'error')
            return redirect(url_for('auth.register'))
        
        if Operator.query.filter_by(mobile=mobile).first():
            flash('यह मोबाइल नंबर पहले से पंजीकृत है', 'error')
            return redirect(url_for('auth.register'))
        
        if Operator.query.filter_by(shop_name=shop_name).first():
            flash('यह दुकान का नाम पहले से पंजीकृत है', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new operator
        operator = Operator(
            full_name=full_name,
            shop_name=shop_name,
            mobile=mobile,
            email=email,
            district=district,
            address=address,
            is_verified=False
        )
        operator.set_password(password)
        operator.generate_verification_token()
        
        # Get free plan
        free_plan = Plan.query.filter_by(name='Free Trial').first()
        if free_plan:
            operator.plan_id = free_plan.id
            operator.subscription_start = datetime.utcnow()
            operator.subscription_end = datetime.utcnow() + timedelta(days=14)
        
        db.session.add(operator)
        db.session.commit()
        
        session['operator_id'] = operator.id
        session['shop_name'] = operator.shop_name
        
        flash('पंजीकरण सफल! आप लॉगिन हो गए हैं।', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me')
        
        if not email or not password:
            flash('ईमेल और पासवर्ड दर्ज करें', 'error')
            return redirect(url_for('auth.login'))
        
        operator = Operator.query.filter_by(email=email).first()
        
        if not operator or not operator.check_password(password):
            flash('ईमेल या पासवर्ड गलत है', 'error')
            return redirect(url_for('auth.login'))
        
        if not operator.is_active:
            flash('आपका खाता निष्क्रिय है', 'error')
            return redirect(url_for('auth.login'))
        
        operator.last_login = datetime.utcnow()
        db.session.commit()
        
        session['operator_id'] = operator.id
        session['shop_name'] = operator.shop_name
        
        if remember_me:
            session.permanent = True
        
        flash(f'स्वागत है, {operator.full_name}!', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('आप लॉगआउट हो गए हैं', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        operator = Operator.query.filter_by(email=email).first()
        if operator:
            operator.generate_verification_token()
            db.session.commit()
            flash('पासवर्ड रीसेट लिंक ईमेल किया गया है', 'success')
            # In production, send email with reset link
        else:
            flash('इस ईमेल से कोई खाता नहीं मिला', 'error')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if len(password) < 8:
            flash('पासवर्ड कम से कम 8 वर्णों का होना चाहिए', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        if password != confirm_password:
            flash('पासवर्ड मेल नहीं खाते', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        operator = Operator.query.filter_by(verification_token=token).first()
        if not operator:
            flash('अमान्य या समाप्त लिंक', 'error')
            return redirect(url_for('auth.login'))
        
        operator.set_password(password)
        operator.verification_token = None
        db.session.commit()
        
        flash('पासवर्ड सफलतापूर्वक बदल दिया गया', 'success')
        return redirect(url_for('auth.login'))
    
    operator = Operator.query.filter_by(verification_token=token).first()
    if not operator:
        flash('अमान्य या समाप्त लिंक', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)
