from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import logging

logger = logging.getLogger(__name__)
pdf_tools_bp = Blueprint('pdf_tools', __name__, url_prefix='/pdf-tools')

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 50 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@pdf_tools_bp.route('/')
def index():
    try:
        return render_template('pdf_tools/index.html')
    except Exception as e:
        logger.error(f'PDF tools error: {e}')
        flash('त्रुटि', 'error')
        return redirect(url_for('index'))
