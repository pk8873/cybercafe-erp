from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from app import db
from models import Operator, Customer, Service
from datetime import datetime

customer_bp = Blueprint('customer', __name__, url_prefix='/dashboard/customers')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'operator_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@customer_bp.route('/')
@login_required
def index():
    operator = Operator.query.get(session['operator_id'])
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Customer.query.filter_by(operator_id=operator.id)
    
    if search:
        query = query.filter(
            (Customer.full_name.ilike(f'%{search}%')) |
            (Customer.mobile.ilike(f'%{search}%')) |
            (Customer.aadhaar_last4.ilike(f'%{search}%'))
        )
    
    customers = query.order_by(Customer.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('dashboard/customers/list.html',
                         customers=customers,
                         search=search)

@customer_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        operator = Operator.query.get(session['operator_id'])
        
        full_name = request.form.get('full_name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        aadhaar_last4 = request.form.get('aadhaar_last4', '').strip()
        address = request.form.get('address', '').strip()
        village = request.form.get('village', '').strip()
        district = request.form.get('district', '').strip()
        notes = request.form.get('notes', '').strip()
        
        if not full_name or not mobile:
            flash('नाम और मोबाइल नंबर दर्ज करें', 'error')
            return redirect(url_for('customer.add'))
        
        customer = Customer(
            operator_id=operator.id,
            full_name=full_name,
            mobile=mobile,
            aadhaar_last4=aadhaar_last4,
            address=address,
            village=village,
            district=district,
            notes=notes
        )
        
        db.session.add(customer)
        db.session.commit()
        
        flash('ग्राहक सफलतापूर्वक जोड़ा गया', 'success')
        return redirect(url_for('customer.index'))
    
    return render_template('dashboard/customers/add.html')

@customer_bp.route('/<int:customer_id>')
@login_required
def view(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    if customer.operator_id != session.get('operator_id'):
        flash('आपको यह ग्राहक देखने की अनुमति नहीं है', 'error')
        return redirect(url_for('customer.index'))
    
    services = Service.query.filter_by(customer_id=customer_id).order_by(
        Service.created_at.desc()
    ).all()
    
    return render_template('dashboard/customers/view.html',
                         customer=customer,
                         services=services)

@customer_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    if customer.operator_id != session.get('operator_id'):
        flash('आपको यह ग्राहक संपादित करने की अनुमति नहीं है', 'error')
        return redirect(url_for('customer.index'))
    
    if request.method == 'POST':
        customer.full_name = request.form.get('full_name', '').strip()
        customer.mobile = request.form.get('mobile', '').strip()
        customer.aadhaar_last4 = request.form.get('aadhaar_last4', '').strip()
        customer.address = request.form.get('address', '').strip()
        customer.village = request.form.get('village', '').strip()
        customer.district = request.form.get('district', '').strip()
        customer.notes = request.form.get('notes', '').strip()
        customer.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('ग्राहक सफलतापूर्वक अपडेट किया गया', 'success')
        return redirect(url_for('customer.view', customer_id=customer_id))
    
    return render_template('dashboard/customers/edit.html', customer=customer)

@customer_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    if customer.operator_id != session.get('operator_id'):
        flash('आपको यह ग्राहक हटाने की अनुमति नहीं है', 'error')
        return redirect(url_for('customer.index'))
    
    db.session.delete(customer)
    db.session.commit()
    
    flash('ग्राहक सफलतापूर्वक हटाया गया', 'success')
    return redirect(url_for('customer.index'))
