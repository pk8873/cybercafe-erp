from flask import Blueprint, render_template, session, redirect, url_for
from models import Payment, Service
from app import db
from functools import wraps
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'operator_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@reports_bp.route('/daily')
@login_required
def daily():
    try:
        operator_id = session.get('operator_id')
        today = datetime.utcnow().date()
        
        daily_earnings = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.operator_id == operator_id,
            db.func.date(Payment.created_at) == today
        ).scalar() or 0
        
        return render_template('reports/daily.html', earnings=daily_earnings)
    except Exception as e:
        logger.error(f'Daily report error: {e}')
        return render_template('errors/500.html', error=str(e))
