from .auth import auth_bp
from .dashboard import dashboard_bp
from .customer import customer_bp
from .service import service_bp
from .admin import admin_bp
from .pdf_tools import pdf_tools_bp
from .reports import reports_bp
from .api import api_bp

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
