from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from functools import wraps
from app import db
from models import Operator, Customer, Service, Document, Payment, Notification, Receipt
from datetime import datetime
import os
from werkzeug.utils import secure_filename

service_bp = Blueprint('service', __name__, url_prefix='/dashboard/services')

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'operator_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

SERVICE_TYPES = [
    'आय प्रमाण पत्र',
    'जाति प्रमाण पत्र',
    'निवास प्रमाण पत्र',
    'पैन कार्ड',
    'छात्रवृत्ति',
    'रेलवे टिकट',
    'आधार प्रिंट',
    'लैमिनेशन',
    'फोटो प्रिंट',
    'ऑनलाइन फॉर्म',
    'आयुष्मान कार्ड',
    'वोटर आईडी',
    'पासपोर्ट फॉर्म'
]

STATUS_CHOICES = ['Pending', 'Submitted', 'Approved', 'Rejected', 'Completed']

@service_bp.route('/')
@login_required
def index():
    operator = Operator.query.get(session['operator_id'])
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = Service.query.filter_by(operator_id=operator.id)
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.join(Customer).filter(
            Customer.full_name.ilike(f'%{search}%')
        )
    
    services = query.order_by(Service.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('dashboard/services/list.html',
                         services=services,
                         status=status,
                         search=search,
                         statuses=STATUS_CHOICES)

@service_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    operator = Operator.query.get(session['operator_id'])
    
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        service_type = request.form.get('service_type')
        payment_amount = request.form.get('payment_amount')
        description = request.form.get('description')
        notes = request.form.get('notes')
        
        if not customer_id or not service_type or not payment_amount:
            flash('सभी आवश्यक फील्ड भरें', 'error')
            return redirect(url_for('service.add'))
        
        try:
            payment_amount = float(payment_amount)
        except ValueError:
            flash('वैध राशि दर्ज करें', 'error')
            return redirect(url_for('service.add'))
        
        service = Service(
            operator_id=operator.id,
            customer_id=customer_id,
            service_type=service_type,
            payment_amount=payment_amount,
            description=description,
            notes=notes,
            status='Pending'
        )
        
        db.session.add(service)
        db.session.commit()
        
        # Create notification
        notification = Notification(
            operator_id=operator.id,
            title='नई सेवा जोड़ी गई',
            message=f'{service_type} सेवा जोड़ी गई',
            notification_type='info'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('सेवा सफलतापूर्वक जोड़ी गई', 'success')
        return redirect(url_for('service.view', service_id=service.id))
    
    customers = Customer.query.filter_by(operator_id=operator.id).all()
    return render_template('dashboard/services/add.html',
                         customers=customers,
                         service_types=SERVICE_TYPES)

@service_bp.route('/<int:service_id>')
@login_required
def view(service_id):
    service = Service.query.get_or_404(service_id)
    
    if service.operator_id != session.get('operator_id'):
        flash('आपको यह सेवा देखने की अनुमति नहीं है', 'error')
        return redirect(url_for('service.index'))
    
    documents = Document.query.filter_by(service_id=service_id).all()
    payments = Payment.query.filter_by(service_id=service_id).all()
    
    return render_template('dashboard/services/view.html',
                         service=service,
                         documents=documents,
                         payments=payments,
                         statuses=STATUS_CHOICES)

@service_bp.route('/<int:service_id>/upload', methods=['POST'])
@login_required
def upload_document(service_id):
    service = Service.query.get_or_404(service_id)
    
    if service.operator_id != session.get('operator_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'कोई फाइल नहीं'}), 400
    
    file = request.files['file']
    document_type = request.form.get('document_type', 'Other')
    
    if file.filename == '':
        return jsonify({'error': 'कोई फाइल नहीं'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'फाइल प्रकार अनुमत नहीं है'}), 400
    
    if len(file.read()) > MAX_FILE_SIZE:
        return jsonify({'error': 'फाइल बहुत बड़ी है'}), 400
    
    file.seek(0)
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}_{filename}"
    
    upload_path = os.path.join('uploads', str(service_id))
    os.makedirs(upload_path, exist_ok=True)
    
    file_path = os.path.join(upload_path, filename)
    file.save(file_path)
    
    # Create document record
    document = Document(
        service_id=service_id,
        document_type=document_type,
        filename=filename,
        file_path=file_path,
        original_name=request.files['file'].filename
    )
    
    db.session.add(document)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'फाइल सफलतापूर्वक अपलोड की गई'})

@service_bp.route('/<int:service_id>/status', methods=['POST'])
@login_required
def update_status(service_id):
    service = Service.query.get_or_404(service_id)
    
    if service.operator_id != session.get('operator_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    new_status = request.json.get('status')
    
    if new_status not in STATUS_CHOICES:
        return jsonify({'error': 'Invalid status'}), 400
    
    service.status = new_status
    if new_status == 'Completed':
        service.completion_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'स्थिति अपडेट की गई'})

@service_bp.route('/<int:service_id>/delete', methods=['POST'])
@login_required
def delete(service_id):
    service = Service.query.get_or_404(service_id)
    
    if service.operator_id != session.get('operator_id'):
        flash('आपको यह सेवा हटाने की अनुमति नहीं है', 'error')
        return redirect(url_for('service.index'))
    
    db.session.delete(service)
    db.session.commit()
    
    flash('सेवा सफलतापूर्वक हटाई गई', 'success')
    return redirect(url_for('service.index'))
