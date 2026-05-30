from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from models import Operator, Plan
from app import db
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

BIHAR_DISTRICTS = [
    'पटना', 'नालंदा', 'गया', 'भागलपुर', 'मुजफ्फरपुर', 'दरभंगा', 'पूर्णिया', 'मधुबनी',
    'समस्तीपुर', 'सीतामढ़ी', 'मोतिहारी', 'वैशाली', 'सारण', 'गोपालगंज', 'सिवान', 'कटिहार',
    'खगड़िया', 'बिहार शरीफ', 'अरवल', 'जहानाबाद', 'औरंगाबाद', 'नवादा', 'बाँका', 'लखीसराय',
    'शेखपुरा', 'किशनगंज', 'अररिया', 'पूर्व चंपारण', 'पश्चिम चंपारण', 'बेतिया', 'मधेपुरा',
    'सुपौल', 'महिषासंध', 'जमुई', 'कोडरमा', 'गिरिडीह', 'धनबाद', 'बोकारो', 'देवघर'
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'operator_id' not in session:
            flash('कृपया पहले लॉगिन करें।', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])\ndef register():
    try:
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            shop_name = request.form.get('shop_name', '').strip()
            mobile = request.form.get('mobile', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            district = request.form.get('district', '').strip()
            address = request.form.get('address', '').strip()

            if not all([full_name, shop_name, mobile, email, password, district]):
                flash('सभी फील्ड भरें।', 'error')
                return render_template('auth/register.html', districts=BIHAR_DISTRICTS)

            # Check if email already exists
            existing = Operator.query.filter_by(email=email).first()
            if existing:
                flash('यह ईमेल पहले से रजिस्टर है।', 'error')
                return render_template('auth/register.html', districts=BIHAR_DISTRICTS)

            try:
                # Create new operator
                operator = Operator(
                    full_name=full_name,
                    shop_name=shop_name,
                    mobile=mobile,
                    email=email,
                    district=district,
                    address=address,
                    is_verified=True
                )
                operator.set_password(password)
                
                # Set default plan - Free Trial for 30 days
                operator.subscription_start = datetime.utcnow()
                operator.subscription_end = datetime.utcnow() + timedelta(days=30)
                
                db.session.add(operator)
                db.session.flush()  # Get the ID without committing
                
                # Create or get Free Trial plan
                try:
                    plan = Plan.query.filter_by(name='Free Trial').first()
                    if not plan:
                        plan = Plan(
                            name='Free Trial',
                            description='30 दिन की निःशुल्क परीक्षा',
                            monthly_price=0.0,
                            yearly_price=0.0,
                            max_customers=100,
                            max_services=1000,
                            storage_gb=5,
                            active=True
                        )
                        db.session.add(plan)
                        db.session.flush()
                    
                    operator.plan_id = plan.id
                except Exception as plan_error:
                    logger.error(f'Plan creation error: {plan_error}')
                    pass
                
                db.session.commit()
                
                logger.info(f'New operator registered: {email}')
                flash('रजिस्ट्रेशन सफल! अब लॉगिन करें।', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                db.session.rollback()
                logger.error(f'Registration error: {str(e)}', exc_info=True)
                flash(f'रजिस्ट्रेशन में त्रुटि: {str(e)}', 'error')
                return render_template('auth/register.html', districts=BIHAR_DISTRICTS)

        return render_template('auth/register.html', districts=BIHAR_DISTRICTS)
        
    except Exception as e:
        logger.error(f'Register page error: {str(e)}', exc_info=True)
        flash('कोई त्रुटि हुई।', 'error')
        return redirect(url_for('index'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')

            if not email or not password:
                flash('ईमेल और पासवर्ड दोनों दर्ज करें।', 'error')
                return render_template('auth/login.html')

            operator = Operator.query.filter_by(email=email).first()

            if operator and operator.check_password(password):
                if not operator.is_active:
                    flash('आपका खाता निलंबित है।', 'error')
                    return render_template('auth/login.html')

                session['operator_id'] = operator.id
                session['operator_name'] = operator.full_name
                session['shop_name'] = operator.shop_name
                operator.last_login = datetime.utcnow()
                
                try:
                    db.session.commit()
                except:
                    db.session.rollback()

                logger.info(f'Operator logged in: {email}')
                flash(f'स्वागत है, {operator.full_name}!', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash('गलत ईमेल या पासवर्ड।', 'error')
                return render_template('auth/login.html')

        return render_template('auth/login.html')
        
    except Exception as e:
        logger.error(f'Login error: {str(e)}', exc_info=True)
        flash('लॉगिन में त्रुटि।', 'error')
        return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('आप लॉगआउट कर दिए गए।', 'success')
    return redirect(url_for('index'))
