from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import Customer, Operator
from app import db
from functools import wraps
import logging

logger = logging.getLogger(__name__)
customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

BIHAR_DISTRICTS = ['पटना', 'नालंदा', 'गया', 'भागलपुर', 'मुजफ्फरपुर', 'दरभंगा', 'पूर्णिया', 'मधुबनी']

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'operator_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@customer_bp.route('/list')
@login_required
def list():
    try:
        operator_id = session.get('operator_id')
        customers = Customer.query.filter_by(operator_id=operator_id).all()
        return render_template('customer/list.html', customers=customers)
    except Exception as e:
        logger.error(f'Customer list error: {e}')
        flash('त्रुटि: ग्राहक सूची लोड नहीं कर सके।', 'error')
        return redirect(url_for('dashboard.index'))

@customer_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    try:
        if request.method == 'POST':
            operator_id = session.get('operator_id')
            full_name = request.form.get('full_name', '').strip()
            mobile = request.form.get('mobile', '').strip()
            aadhaar_last4 = request.form.get('aadhaar_last4', '').strip()
            address = request.form.get('address', '').strip()
            village = request.form.get('village', '').strip()
            district = request.form.get('district', '').strip()

            if not full_name or not mobile:
                flash('नाम और मोबाइल दोनों आवश्यक हैं।', 'error')
                return redirect(url_for('customer.add'))

            try:
                customer = Customer(
                    operator_id=operator_id,
                    full_name=full_name,
                    mobile=mobile,
                    aadhaar_last4=aadhaar_last4,
                    address=address,
                    village=village,
                    district=district
                )
                db.session.add(customer)
                db.session.commit()
                flash('ग्राहक जोड़ा गया।', 'success')
                return redirect(url_for('customer.list'))
            except Exception as e:
                db.session.rollback()
                logger.error(f'Add customer error: {e}')
                flash('ग्राहक जोड़ने में त्रुटि।', 'error')
                return redirect(url_for('customer.add'))

        return render_template('customer/add.html', districts=BIHAR_DISTRICTS)
    except Exception as e:
        logger.error(f'Customer add page error: {e}')
        flash('त्रुटि', 'error')
        return redirect(url_for('dashboard.index'))

@customer_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    try:
        customer = Customer.query.get(id)
        if not customer or customer.operator_id != session.get('operator_id'):
            return redirect(url_for('customer.list'))

        if request.method == 'POST':
            customer.full_name = request.form.get('full_name', '').strip()
            customer.mobile = request.form.get('mobile', '').strip()
            customer.address = request.form.get('address', '').strip()
            customer.district = request.form.get('district', '').strip()
            customer.village = request.form.get('village', '').strip()
            
            db.session.commit()
            flash('ग्राहक अपडेट किया गया।', 'success')
            return redirect(url_for('customer.list'))

        return render_template('customer/edit.html', customer=customer, districts=BIHAR_DISTRICTS)
    except Exception as e:
        logger.error(f'Edit customer error: {e}')
        flash('त्रुटि', 'error')
        return redirect(url_for('customer.list'))

@customer_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    try:
        customer = Customer.query.get(id)
        if customer and customer.operator_id == session.get('operator_id'):
            db.session.delete(customer)
            db.session.commit()
            flash('ग्राहक हटा दिया गया।', 'success')
        return redirect(url_for('customer.list'))
    except Exception as e:
        logger.error(f'Delete customer error: {e}')
        flash('ग्राहक हटाने में त्रुटि।', 'error')
        return redirect(url_for('customer.list'))
