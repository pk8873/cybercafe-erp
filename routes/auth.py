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
    'अरारिया', 'अरवल', 'औरंगाबाद', 'बाँका', 'बारां', 'बारिपुर', 'बेतिया', 'बिहार शरीफ',
    'भागलपुर', 'बिक्रमगंज', 'बिंदु', 'बोधगया', 'बिहारीगंज', 'चम्पारण', 'छपरा', 'दरभंगा',
    'डेहरी ऑन सोन', 'देव', 'धनबाद', 'दिलदारनगर', 'दिल्लीपुर', 'दिमापुर', 'दीक्षा',
    'गंगा पार', 'गया', 'गोपालगंज', 'हजारीबाग', 'हसन', 'हाजीपुर', 'हिमाचल', 'जमालपुर',
    'जनकपुर', 'जहानाबाद', 'जलालपुर', 'जलेश्वर', 'जमुई', 'जयनगर', 'जयपुरघाट', 'जेतपुर',
    'खगड़िया', 'खीरा', 'कटिहार', 'किशनगंज', 'कोडरमा', 'कुमारहट', 'लखीसराय', 'लक्षद्वीप',
    'लालगंज', 'लक्ष्मी नारायण पुर', 'मधेपुरा', 'मधुबनी', 'महिषा', 'मैनपुरी', 'मखदुमपुर',
    'मालदा', 'मामलपुर', 'मुंगेर', 'मुज़फ़्फ़रपुर', 'मेहसी', 'मेहता', 'मिथिलांचल', 'मिथिला',
    'मो. आरपुर', 'मुसलमपुर', 'मोतिहारी', 'मोहनीया', 'नई दिल्ली', 'नवादा', 'नार्थ 24 परगना',
    'नवीनगर', 'नयानगर', 'नलंदा', 'नेवादा', 'नेवाड़ी', 'नीलांचल', 'पटना', 'पटारी', 'पटेल',
    'पंडारी', 'पंडौल', 'पापली', 'पसरई', 'पिपिली', 'पीरो', 'पोखरवा', 'पूर्ब चंपारण', 'पूर्णिया',
    'पूसा', 'रघुनाथपुर', 'राजपुर', 'रामपुर', 'रामपुरवा', 'रामसरी', 'राणा', 'रांची', 'रांगली',
    'रातू', 'रायगंज', 'रेवती', 'रिसुआ', 'रोहतास', 'साकरी', 'सकरी', 'सलेमपुर', 'सांतान',
    'सपौल', 'सारण', 'सास्टी', 'सातपुरा', 'सेखपुरा', 'सेमरी', 'सेमरीमास', 'सेनुआर', 'शाहपुर',
    'शांतिनगर', 'शेरघाटी', 'शेरपुर', 'शिमला', 'शिवपालपुर', 'शिवहर', 'शोहरतगड़', 'सिमरिया',
    'सिमरिया खुर्द', 'सिमरीमास', 'सिमरीया', 'सिमुलतला', 'सिंघुआ', 'सिंघुआ पूर', 'सिंघुआ पश्चिम',
    'सिंहभूम', 'सिंहपुर', 'सिराज', 'सिरसिया', 'सिसवां', 'सितामढ़ी', 'सीतामरही', 'सीतामारी',
    'सीतामरी', 'सीतापुर', 'सीवान', 'सोन', 'सोनपुर', 'सोनारंजन', 'सोरी', 'सुकारी', 'सुकेत',
    'सुल्तान', 'सुल्तानपुर', 'सुल्तानपुरा', 'सुमारी', 'सुमारी दक्षिण', 'सुमारी पूर्व', 'सुमारी पश्चिम',
    'सुमारी उत्तर', 'सुमेरपुर', 'सुमेरपुरा', 'सुमेरिया', 'सुमैर', 'सुमैरा', 'सुहुलपुरा', 'सुहुलपुरी',
    'सुहुलपुरीया', 'सुहुलदास', 'सुहुलदि', 'सुहुलहाजी', 'सुहुलहाली', 'सुहुलहा', 'सुहुलिया',
    'सुहुलिई', 'सुहुलिया', 'सुहुले', 'सुहुलेश्वर', 'सुहुलिया', 'सुहुलह', 'सुहुलदी', 'सुहुलदू',
    'सुहुलदे', 'सुहुलदै', 'सुहुलदो', 'सुहुलदी', 'सुहुली', 'सुहुलू', 'सुहुलि', 'सुहुलु',
    'सुहुला', 'सुहुली', 'सुहुले', 'सुहुलै', 'सुहुलो', 'सुहुलु', 'सुहुलो', 'सुहुलु', 'सुहुला',
    'सुहुली', 'सुहुले', 'सुहुली', 'सुहुली', 'सुहुले', 'सुहुली', 'सुहुली', 'सुहुले', 'सुहुली',
    'सुहुली', 'सुहुली', 'सुहुले', 'सुहुली', 'सुहुली', 'सुहुले', 'सुहुली', 'सुहुली', 'सुहुले',
    'तारापुर', 'तारातला', 'तारेय', 'तारिकेश', 'तारिकेश पूर', 'तारिकेश पश्चिम', 'तारीख',
    'ताराखर', 'ताराग़र', 'तारागर', 'तारागरपुर', 'तारागर', 'तारागर', 'तारागर', 'तारागर',
    'तारागर', 'तारागर', 'तारागर', 'तारागर', 'तारागर', 'तारागर', 'तारागर', 'तारागर'
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'operator_id' not in session:
            flash('कृपया पहले लॉगिन करें।', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
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
                return redirect(url_for('auth.register'))

            if Operator.query.filter_by(email=email).first():
                flash('यह ईमेल पहले से रजिस्टर है।', 'error')
                return redirect(url_for('auth.register'))

            try:
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
                
                default_plan = Plan.query.filter_by(name='Free Trial').first()
                if default_plan:
                    operator.plan_id = default_plan.id
                    operator.subscription_end = datetime.utcnow() + timedelta(days=30)
                
                db.session.add(operator)
                db.session.commit()
                
                flash('रजिस्ट्रेशन सफल! अब लॉगिन करें।', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                logger.error(f'Registration error: {e}')
                flash('रजिस्ट्रेशन में त्रुटि।', 'error')
                return redirect(url_for('auth.register'))

        return render_template('auth/register.html', districts=BIHAR_DISTRICTS)
    except Exception as e:
        logger.error(f'Register page error: {e}')
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
                return redirect(url_for('auth.login'))

            operator = Operator.query.filter_by(email=email).first()

            if operator and operator.check_password(password):
                if not operator.is_active:
                    flash('आपका खाता निलंबित है।', 'error')
                    return redirect(url_for('auth.login'))

                session['operator_id'] = operator.id
                session['operator_name'] = operator.full_name
                session['shop_name'] = operator.shop_name
                operator.last_login = datetime.utcnow()
                db.session.commit()

                flash(f'स्वागत है, {operator.full_name}!', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash('गलत ईमेल या पासवर्ड।', 'error')
                return redirect(url_for('auth.login'))

        return render_template('auth/login.html')
    except Exception as e:
        logger.error(f'Login error: {e}')
        flash('लॉगिन में त्रुटि।', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('आप लॉगआउट कर दिए गए।', 'success')
    return redirect(url_for('index'))
