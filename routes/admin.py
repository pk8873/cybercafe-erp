from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime
from app import db
from models import Operator, Customer, Service, Payment, Plan, Complaint, AdminLog, Notification
from werkzeug.security import generate_password_hash
import os

admin_bp = Blueprint('admin', __name__, url_prefix='')

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin@123')

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin login required', 'error')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/secure-admin-panel-login', methods=['GET', 'POST'])
def admin_login():
    # Hidden admin login - NOT visible on homepage or public pages
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_id'] = 'admin'
            session['admin_username'] = username
            
            log = AdminLog(action='Admin Login', details=f'Admin {username} logged in')
            db.session.add(log)
            db.session.commit()
            
            flash('Admin logged in successfully', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('admin.admin_login'))
    
    return render_template('admin/login.html')

@admin_bp.route('/secure-admin-dashboard')
@admin_login_required
def admin_dashboard():
    total_operators = Operator.query.count()
    active_operators = Operator.query.filter_by(is_active=True).count()
    total_customers = Customer.query.count()
    
    # Revenue calculation
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.status == 'Completed'
    ).scalar() or 0
    
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    today_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.created_at >= today_start,
        Payment.created_at <= today_end,
        Payment.status == 'Completed'
    ).scalar() or 0
    
    stats = {
        'total_operators': total_operators,
        'active_operators': active_operators,
        'total_customers': total_customers,
        'total_revenue': round(total_revenue, 2),
        'today_revenue': round(today_revenue, 2)
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/secure-admin-operators')
@admin_login_required
def manage_operators():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Operator.query
    
    if search:
        query = query.filter(
            (Operator.full_name.ilike(f'%{search}%')) |
            (Operator.shop_name.ilike(f'%{search}%')) |
            (Operator.email.ilike(f'%{search}%'))
        )
    
    operators = query.order_by(Operator.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/operators.html', operators=operators, search=search)

@admin_bp.route('/secure-admin-operators/<int:operator_id>/suspend', methods=['POST'])
@admin_login_required
def suspend_operator(operator_id):
    operator = Operator.query.get_or_404(operator_id)
    operator.is_active = False
    
    log = AdminLog(
        action='Operator Suspended',
        details=f'Operator {operator.shop_name} suspended'
    )
    
    db.session.add(log)
    db.session.commit()
    
    flash(f'{operator.shop_name} suspended', 'success')
    return redirect(url_for('admin.manage_operators'))

@admin_bp.route('/secure-admin-operators/<int:operator_id>/activate', methods=['POST'])
@admin_login_required
def activate_operator(operator_id):
    operator = Operator.query.get_or_404(operator_id)
    operator.is_active = True
    
    log = AdminLog(
        action='Operator Activated',
        details=f'Operator {operator.shop_name} activated'
    )
    
    db.session.add(log)
    db.session.commit()
    
    flash(f'{operator.shop_name} activated', 'success')
    return redirect(url_for('admin.manage_operators'))

@admin_bp.route('/secure-admin-operators/<int:operator_id>/delete', methods=['POST'])
@admin_login_required
def delete_operator(operator_id):
    operator = Operator.query.get_or_404(operator_id)
    
    log = AdminLog(
        action='Operator Deleted',
        details=f'Operator {operator.shop_name} deleted'
    )
    
    db.session.delete(operator)
    db.session.add(log)
    db.session.commit()
    
    flash(f'{operator.shop_name} deleted', 'success')
    return redirect(url_for('admin.manage_operators'))

@admin_bp.route('/secure-admin-complaints')
@admin_login_required
def manage_complaints():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Complaint.query
    
    if status:
        query = query.filter_by(status=status)
    
    complaints = query.order_by(Complaint.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/complaints.html', complaints=complaints, status=status)

@admin_bp.route('/secure-admin-complaints/<int:complaint_id>/reply', methods=['POST'])
@admin_login_required
def reply_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    reply = request.form.get('reply', '')
    
    complaint.admin_reply = reply
    complaint.status = 'Closed'
    
    notification = Notification(
        operator_id=complaint.operator_id,
        title='शिकायत का जवाब',
        message=f'आपकी शिकायत का जवाब दिया गया है',
        notification_type='info'
    )
    
    db.session.add(notification)
    db.session.commit()
    
    flash('Reply sent', 'success')
    return redirect(url_for('admin.manage_complaints'))

@admin_bp.route('/secure-admin-plans')
@admin_login_required
def manage_plans():
    plans = Plan.query.all()
    return render_template('admin/plans.html', plans=plans)

@admin_bp.route('/secure-admin-plans/<int:plan_id>/edit', methods=['POST'])
@admin_login_required
def edit_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    
    plan.monthly_price = float(request.form.get('monthly_price', plan.monthly_price))
    plan.yearly_price = float(request.form.get('yearly_price', plan.yearly_price))
    
    log = AdminLog(
        action='Plan Updated',
        details=f'Plan {plan.name} updated'
    )
    
    db.session.add(log)
    db.session.commit()
    
    flash('Plan updated', 'success')
    return redirect(url_for('admin.manage_plans'))

@admin_bp.route('/secure-admin-logout')
def admin_logout():
    session.clear()
    flash('Admin logged out', 'success')
    return redirect(url_for('index'))
