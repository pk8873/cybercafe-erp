from flask import Blueprint, render_template, session
from functools import wraps
from models import Operator, Customer, Service, Payment
from app import db
from datetime import datetime
from flask import redirect, url_for
import logging

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'operator_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@dashboard_bp.route('/')
@login_required
def index():
    try:
        operator_id = session.get('operator_id')
        operator = Operator.query.get(operator_id)
        
        if not operator:
            return redirect(url_for('auth.login'))
        
        total_customers = Customer.query.filter_by(operator_id=operator_id).count()
        total_services = Service.query.filter_by(operator_id=operator_id).count()
        today_earnings = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.operator_id == operator_id,
            db.func.date(Payment.created_at) == datetime.utcnow().date()
        ).scalar() or 0
        
        pending_services = Service.query.filter_by(operator_id=operator_id, status='Pending').count()
        completed_services = Service.query.filter_by(operator_id=operator_id, status='Completed').count()
        
        return render_template('dashboard/index.html',
            operator=operator,
            total_customers=total_customers,
            total_services=total_services,
            today_earnings=today_earnings,
            pending_services=pending_services,
            completed_services=completed_services
        )
    except Exception as e:
        logger.error(f'Dashboard error: {e}')
        return render_template('errors/500.html', error=str(e))
