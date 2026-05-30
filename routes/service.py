from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Service, Customer, Payment
from app import db
from functools import wraps
import logging

logger = logging.getLogger(__name__)
service_bp = Blueprint('service', __name__, url_prefix='/service')

SERVICE_TYPES = [
    'आय प्रमाण पत्र',
    'जाति प्रमाण पत्र', 
    'निवास प्रमाण पत्र',
    'पैन कार्ड',
    'छात्रवृत्ति',
    'रेलवे टिकट',
    'आधार प्रिंट',
    'लेमिनेशन',
    'फोटो प्रिंट',
    'ऑनलाइन फॉर्म',
    'आयुष्मान कार्ड',
    'वोटर ID',
    'पासपोर्ट फॉर्म'
]

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'operator_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@service_bp.route('/list')
@login_required
def list():
    try:
        operator_id = session.get('operator_id')
        services = Service.query.filter_by(operator_id=operator_id).all()
        return render_template('service/list.html', services=services)
    except Exception as e:
        logger.error(f'Service list error: {e}')
        flash('सेवा सूची लोड में त्रुटि।', 'error')
        return redirect(url_for('dashboard.index'))

@service_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    try:
        operator_id = session.get('operator_id')
        customers = Customer.query.filter_by(operator_id=operator_id).all()
        
        if request.method == 'POST':
            customer_id = request.form.get('customer_id')
            service_type = request.form.get('service_type', '').strip()
            payment_amount = request.form.get('payment_amount', 0)
            
            try:
                service = Service(
                    operator_id=operator_id,
                    customer_id=int(customer_id),
                    service_type=service_type,
                    payment_amount=float(payment_amount),
                    status='Pending'
                )
                db.session.add(service)
                db.session.commit()
                flash('सेवा जोड़ी गई।', 'success')
                return redirect(url_for('service.list'))
            except Exception as e:
                db.session.rollback()
                logger.error(f'Add service error: {e}')
                flash('सेवा जोड़ने में त्रुटि।', 'error')

        return render_template('service/add.html', customers=customers, service_types=SERVICE_TYPES)
    except Exception as e:
        logger.error(f'Service add page error: {e}')
        flash('त्रुटि', 'error')
        return redirect(url_for('dashboard.index'))

@service_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    try:
        service = Service.query.get(id)
        if not service or service.operator_id != session.get('operator_id'):
            return redirect(url_for('service.list'))

        if request.method == 'POST':
            service.service_type = request.form.get('service_type', '').strip()
            service.status = request.form.get('status', 'Pending')
            service.payment_amount = float(request.form.get('payment_amount', 0))
            db.session.commit()
            flash('सेवा अपडेट की गई।', 'success')
            return redirect(url_for('service.list'))

        return render_template('service/edit.html', service=service, service_types=SERVICE_TYPES)
    except Exception as e:
        logger.error(f'Edit service error: {e}')
        flash('त्रुटि', 'error')
        return redirect(url_for('service.list'))
