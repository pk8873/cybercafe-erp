from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta
from app import db
from models import Operator, Customer, Service, Payment, Notification

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'operator_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/')
@login_required
def index():
    operator = Operator.query.get(session['operator_id'])
    if not operator:
        return redirect(url_for('auth.login'))
    
    # Get statistics
    total_customers = Customer.query.filter_by(operator_id=operator.id).count()
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    today_earnings = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.operator_id == operator.id,
        Payment.created_at >= today_start,
        Payment.created_at <= today_end,
        Payment.status == 'Completed'
    ).scalar() or 0
    
    pending_services = Service.query.filter_by(
        operator_id=operator.id,
        status='Pending'
    ).count()
    
    completed_services = Service.query.filter_by(
        operator_id=operator.id,
        status='Completed'
    ).count()
    
    # Get recent activities
    recent_services = Service.query.filter_by(operator_id=operator.id).order_by(
        Service.created_at.desc()
    ).limit(5).all()
    
    # Get notifications
    notifications = Notification.query.filter_by(
        operator_id=operator.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    stats = {
        'total_customers': total_customers,
        'today_earnings': round(today_earnings, 2),
        'pending_services': pending_services,
        'completed_services': completed_services,
        'subscription_days': operator.get_days_remaining()
    }
    
    return render_template('dashboard/index.html',
                         operator=operator,
                         stats=stats,
                         recent_services=recent_services,
                         notifications=notifications)

@dashboard_bp.route('/notifications')
@login_required
def notifications():
    operator = Operator.query.get(session['operator_id'])
    if not operator:
        return redirect(url_for('auth.login'))
    
    notifications = Notification.query.filter_by(
        operator_id=operator.id
    ).order_by(Notification.created_at.desc()).all()
    
    # Mark as read
    for notif in notifications:
        if not notif.is_read:
            notif.is_read = True
    db.session.commit()
    
    return render_template('dashboard/notifications.html', notifications=notifications)

@dashboard_bp.route('/settings')
@login_required
def settings():
    operator = Operator.query.get(session['operator_id'])
    if not operator:
        return redirect(url_for('auth.login'))
    
    return render_template('dashboard/settings.html', operator=operator)

@dashboard_bp.route('/subscription')
@login_required
def subscription():
    operator = Operator.query.get(session['operator_id'])
    if not operator:
        return redirect(url_for('auth.login'))
    
    from models import Plan
    plans = Plan.query.filter_by(active=True).all()
    
    return render_template('dashboard/subscription.html',
                         operator=operator,
                         plans=plans)
