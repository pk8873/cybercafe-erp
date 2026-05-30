from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.customer import customer_bp
from routes.service import service_bp
from routes.admin import admin_bp
from routes.pdf_tools import pdf_tools_bp
from routes.reports import reports_bp
from routes.api import api_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'customer_bp',
    'service_bp',
    'admin_bp',
    'pdf_tools_bp',
    'reports_bp',
    'api_bp'
]
