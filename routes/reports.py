from flask import Blueprint, render_template, request, send_file, session, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta
from app import db
from models import Operator, Service, Payment
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

reports_bp = Blueprint('reports', __name__, url_prefix='/dashboard/reports')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'operator_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@reports_bp.route('/')
@login_required
def index():
    operator = Operator.query.get(session['operator_id'])
    return render_template('dashboard/reports/index.html', operator=operator)

@reports_bp.route('/daily')
@login_required
def daily_report():
    operator = Operator.query.get(session['operator_id'])
    date_str = request.args.get('date')
    
    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = datetime.utcnow().date()
    
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date, datetime.max.time())
    
    services = Service.query.filter_by(operator_id=operator.id).filter(
        Service.created_at >= day_start,
        Service.created_at <= day_end
    ).all()
    
    payments = Payment.query.filter_by(operator_id=operator.id).filter(
        Payment.created_at >= day_start,
        Payment.created_at <= day_end,
        Payment.status == 'Completed'
    ).all()
    
    total_earnings = sum(p.amount for p in payments)
    
    return render_template('dashboard/reports/daily.html',
                         operator=operator,
                         date=target_date,
                         services=services,
                         payments=payments,
                         total_earnings=total_earnings)

@reports_bp.route('/monthly')
@login_required
def monthly_report():
    operator = Operator.query.get(session['operator_id'])
    year = request.args.get('year', type=int) or datetime.utcnow().year
    month = request.args.get('month', type=int) or datetime.utcnow().month
    
    from datetime import date
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)
    
    month_start = datetime.combine(month_start, datetime.min.time())
    month_end = datetime.combine(month_end, datetime.max.time())
    
    services = Service.query.filter_by(operator_id=operator.id).filter(
        Service.created_at >= month_start,
        Service.created_at <= month_end
    ).all()
    
    payments = Payment.query.filter_by(operator_id=operator.id).filter(
        Payment.created_at >= month_start,
        Payment.created_at <= month_end,
        Payment.status == 'Completed'
    ).all()
    
    total_earnings = sum(p.amount for p in payments)
    
    return render_template('dashboard/reports/monthly.html',
                         operator=operator,
                         year=year,
                         month=month,
                         services=services,
                         payments=payments,
                         total_earnings=total_earnings)

@reports_bp.route('/download-pdf')
@login_required
def download_pdf():
    operator = Operator.query.get(session['operator_id'])
    report_type = request.args.get('type', 'monthly')
    
    # Create PDF
    pdf_io = io.BytesIO()
    doc = SimpleDocTemplate(pdf_io, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#333333'),
        alignment=1
    )
    
    # Title
    elements.append(Paragraph(f'आय रिपोर्ट - {operator.shop_name}', title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Report data
    if report_type == 'daily':
        date_str = request.args.get('date')
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = datetime.combine(target_date, datetime.max.time())
        
        payments = Payment.query.filter_by(operator_id=operator.id).filter(
            Payment.created_at >= day_start,
            Payment.created_at <= day_end,
            Payment.status == 'Completed'
        ).all()
    else:
        year = request.args.get('year', type=int) or datetime.utcnow().year
        month = request.args.get('month', type=int) or datetime.utcnow().month
        
        from datetime import date
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
        
        month_start = datetime.combine(month_start, datetime.min.time())
        month_end = datetime.combine(month_end, datetime.max.time())
        
        payments = Payment.query.filter_by(operator_id=operator.id).filter(
            Payment.created_at >= month_start,
            Payment.created_at <= month_end,
            Payment.status == 'Completed'
        ).all()
    
    # Create table
    table_data = [['क्रम', 'राशि', 'विधि', 'तारीख']]
    total = 0
    for i, payment in enumerate(payments, 1):
        table_data.append([
            str(i),
            f'₹{payment.amount:.2f}',
            payment.payment_method or 'N/A',
            payment.created_at.strftime('%d-%m-%Y')
        ])
        total += payment.amount
    
    table_data.append(['कुल', f'₹{total:.2f}', '', ''])
    
    table = Table(table_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F5E9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    pdf_io.seek(0)
    return send_file(
        pdf_io,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'report_{datetime.utcnow().strftime("%Y%m%d")}.pdf'
    )
