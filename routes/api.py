from flask import Blueprint, jsonify, request, session
from models import Customer, Service
from app import db
from functools import wraps
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

def api_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'operator_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@api_bp.route('/customers', methods=['GET'])
@api_login_required
def get_customers():
    try:
        operator_id = session.get('operator_id')
        customers = Customer.query.filter_by(operator_id=operator_id).all()
        return jsonify([{
            'id': c.id,
            'name': c.full_name,
            'mobile': c.mobile,
            'district': c.district
        } for c in customers])
    except Exception as e:
        logger.error(f'API error: {e}')
        return jsonify({'error': 'Server error'}), 500
