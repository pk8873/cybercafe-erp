from flask import Blueprint, jsonify, request, session
from functools import wraps
from app import db
from models import Operator, Customer, Service, Payment, Notification
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'operator_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/customers', methods=['GET'])
@token_required
def get_customers():
    operator = Operator.query.get(session['operator_id'])
    customers = Customer.query.filter_by(operator_id=operator.id).all()
    
    return jsonify([
        {
            'id': c.id,
            'name': c.full_name,
            'mobile': c.mobile,
            'aadhaar_last4': c.aadhaar_last4
        } for c in customers
    ])

@api_bp.route('/services', methods=['GET'])
@token_required
def get_services():
    operator = Operator.query.get(session['operator_id'])
    status = request.args.get('status')
    
    query = Service.query.filter_by(operator_id=operator.id)
    if status:
        query = query.filter_by(status=status)
    
    services = query.all()
    
    return jsonify([
        {
            'id': s.id,
            'customer': s.customer.full_name,
            'type': s.service_type,
            'amount': s.payment_amount,
            'status': s.status,
            'created_at': s.created_at.isoformat()
        } for s in services
    ])

@api_bp.route('/stats', methods=['GET'])
@token_required
def get_stats():
    operator = Operator.query.get(session['operator_id'])
    
    total_customers = Customer.query.filter_by(operator_id=operator.id).count()
    total_services = Service.query.filter_by(operator_id=operator.id).count()
    
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
    
    return jsonify({
        'total_customers': total_customers,
        'total_services': total_services,
        'today_earnings': round(today_earnings, 2),
        'pending_services': pending_services
    })

@api_bp.route('/notifications/unread', methods=['GET'])
@token_required
def get_unread_notifications():
    operator = Operator.query.get(session['operator_id'])
    
    notifications = Notification.query.filter_by(
        operator_id=operator.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    return jsonify([
        {
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.notification_type,
            'created_at': n.created_at.isoformat()
        } for n in notifications
    ])
