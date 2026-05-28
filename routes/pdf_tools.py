from flask import Blueprint, render_template, request, send_file, jsonify, session, redirect, url_for, flash
from functools import wraps
from PIL import Image
import io
import os
from werkzeug.utils import secure_filename
from datetime import datetime
try:
    from PyPDF2 import PdfMerger, PdfReader, PdfWriter
except ImportError:
    from PyPDF2 import PdfFileMerger as PdfMerger, PdfFileReader as PdfReader, PdfFileWriter as PdfWriter

pdf_tools_bp = Blueprint('pdf_tools', __name__, url_prefix='/dashboard/pdf-tools')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'operator_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@pdf_tools_bp.route('/')
@login_required
def index():
    return render_template('dashboard/pdf_tools/index.html')

@pdf_tools_bp.route('/image-resize')
@login_required
def image_resize():
    return render_template('dashboard/pdf_tools/image_resize.html')

@pdf_tools_bp.route('/image-resize/process', methods=['POST'])
@login_required
def process_image_resize():
    if 'file' not in request.files:
        return jsonify({'error': 'कोई फाइल नहीं'}), 400
    
    file = request.files['file']
    width = request.form.get('width', type=int)
    height = request.form.get('height', type=int)
    
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'अमान्य फाइल'}), 400
    
    try:
        img = Image.open(file.stream)
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name='resized_image.png'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_tools_bp.route('/signature-resize')
@login_required
def signature_resize():
    return render_template('dashboard/pdf_tools/signature_resize.html')

@pdf_tools_bp.route('/signature-resize/process', methods=['POST'])
@login_required
def process_signature_resize():
    if 'file' not in request.files:
        return jsonify({'error': 'कोई फाइल नहीं'}), 400
    
    file = request.files['file']
    width = request.form.get('width', 200, type=int)
    height = request.form.get('height', 80, type=int)
    
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'अमान्य फाइल'}), 400
    
    try:
        img = Image.open(file.stream)
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name='signature.png'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_tools_bp.route('/passport-photo')
@login_required
def passport_photo():
    return render_template('dashboard/pdf_tools/passport_photo.html')

@pdf_tools_bp.route('/passport-photo/process', methods=['POST'])
@login_required
def process_passport_photo():
    if 'file' not in request.files:
        return jsonify({'error': 'कोई फाइल नहीं'}), 400
    
    file = request.files['file']
    
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'अमान्य फाइल'}), 400
    
    try:
        img = Image.open(file.stream)
        # Passport photo standard: 2x2 inches at 300 DPI = 600x600 pixels
        img = img.resize((600, 600), Image.Resampling.LANCZOS)
        
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='passport_photo.jpg'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_tools_bp.route('/pdf-merge')
@login_required
def pdf_merge():
    return render_template('dashboard/pdf_tools/pdf_merge.html')

@pdf_tools_bp.route('/pdf-merge/process', methods=['POST'])
@login_required
def process_pdf_merge():
    if 'files' not in request.files:
        return jsonify({'error': 'कोई फाइल नहीं'}), 400
    
    files = request.files.getlist('files')
    
    try:
        merger = PdfMerger()
        
        for file in files:
            if file and file.filename.endswith('.pdf'):
                merger.append(file.stream)
        
        pdf_io = io.BytesIO()
        merger.write(pdf_io)
        merger.close()
        pdf_io.seek(0)
        
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_tools_bp.route('/pdf-compress')
@login_required
def pdf_compress():
    return render_template('dashboard/pdf_tools/pdf_compress.html')

@pdf_tools_bp.route('/pdf-compress/process', methods=['POST'])
@login_required
def process_pdf_compress():
    if 'file' not in request.files:
        return jsonify({'error': 'कोई फाइल नहीं'}), 400
    
    file = request.files['file']
    
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'अमान्य PDF फाइल'}), 400
    
    try:
        reader = PdfReader(file.stream)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        pdf_io = io.BytesIO()
        writer.write(pdf_io)
        pdf_io.seek(0)
        
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='compressed.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
