from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import Operator, Payment
from app import db
from functools import wraps
import logging

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/secure-admin-panel')

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin@123456'

def admin_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                logger.info(f'Admin logged in')
                flash('एडमिन पैनल में स्वागत है।', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                logger.warning(f'Failed admin login attempt with username: {username}')
                flash('गलत यूजरनेम या पासवर्ड।', 'error')
        
        return render_template('admin/login.html')
    except Exception as e:
        logger.error(f'Admin login error: {str(e)}', exc_info=True)
        flash('त्रुटि: ' + str(e), 'error')
        return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@admin_login_required
def dashboard():
    try:
        total_operators = Operator.query.count()
        active_operators = Operator.query.filter_by(is_active=True).count()
        
        # Calculate total revenue from payments
        total_revenue = 0
        try:
            revenue_result = db.session.query(db.func.sum(Payment.amount)).scalar()
            total_revenue = float(revenue_result) if revenue_result else 0
        except:
            total_revenue = 0
        
        return render_template('admin/dashboard.html',
            total_operators=total_operators,
            active_operators=active_operators,
            total_revenue=total_revenue
        )
    except Exception as e:
        logger.error(f'Admin dashboard error: {str(e)}', exc_info=True)
        flash('डैशबोर्ड लोड करने में त्रुटि: ' + str(e), 'error')
        return render_template('errors/500.html', error=str(e))

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    logger.info('Admin logged out')
    flash('एडमिन पैनल से लॉगआउट हो गए।', 'success')
    return redirect(url_for('index'))
