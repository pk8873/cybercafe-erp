# Cyber Cafe Digital Manager - सायबर कैफे डिजिटल मैनेजर

## 🚀 Production Ready SaaS Platform for Bihar Cyber Cafes

Complete management system for cyber cafes, CSC centers, and online form shops in Bihar, India.

### ✨ Features

- ✅ **Operator Registration & Authentication** - Secure login with password hashing
- ✅ **Customer Management** - Track all customers with Aadhaar, address, and notes
- ✅ **Service Management** - 13+ service types (Income Certificate, Caste Certificate, etc.)
- ✅ **Payment Tracking** - Daily, weekly, monthly earnings reports
- ✅ **PDF Tools** - Image resize, signature editing, passport photo crop, PDF merge/split
- ✅ **Receipt Generation** - Automatic PDF receipt generation with QR codes
- ✅ **Admin Panel** - Hidden secure admin dashboard at /secure-admin-panel-login
- ✅ **Bihar Districts** - All 38 districts of Bihar included
- ✅ **Mobile Responsive** - 100% responsive design for all devices
- ✅ **Hindi Language** - Complete Hindi interface for users
- ✅ **Deployment Ready** - One-click deployment on Render.com

### 🛠️ Tech Stack

```
Backend: Python 3.11 + Flask
Database: PostgreSQL
Frontend: HTML5 + Tailwind CSS + Vanilla JavaScript
Deployment: Render.com
ORM: SQLAlchemy
Migrations: Flask-Migrate
```

### 📋 Service Types Included

1. आय प्रमाण पत्र (Income Certificate)
2. जाति प्रमाण पत्र (Caste Certificate)
3. निवास प्रमाण पत्र (Residential Certificate)
4. पैन कार्ड (PAN Card)
5. छात्रवृत्ति (Scholarship)
6. रेलवे टिकट (Railway Ticket)
7. आधार प्रिंट (Aadhaar Print)
8. लेमिनेशन (Lamination)
9. फोटो प्रिंट (Photo Print)
10. ऑनलाइन फॉर्म (Online Form)
11. आयुष्मान कार्ड (Ayushman Card)
12. वोटर ID (Voter ID)
13. पासपोर्ट फॉर्म (Passport Form)

### 🔧 Installation & Setup

#### Local Development

```bash
# Clone repository
git clone https://github.com/pk8873/cybercafe-erp
cd cybercafe-erp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see .env.example)
cp .env.example .env

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Run development server
python app.py
# Visit: http://localhost:5000
```

#### Production Deployment on Render.com

1. Push code to GitHub
2. Connect GitHub repo to Render
3. Set environment variables in Render dashboard
4. Deploy
5. Database will be created automatically

### 👥 Default Admin Credentials

**Username:** `admin`  
**Password:** `admin@123456`

**Change these immediately in production!**

### 📁 Project Structure

```
cybercafe-erp/
├── app.py                 # Main Flask app
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── render.yaml            # Render deployment config
├── Procfile              # Gunicorn config
├── .env.example          # Environment template
│
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Login/Register
│   ├── dashboard.py      # Operator dashboard
│   ├── customer.py       # Customer management
│   ├── service.py        # Service management
│   ├── admin.py          # Admin panel (hidden)
│   ├── pdf_tools.py      # PDF utilities
│   ├── reports.py        # Reports generation
│   └── api.py            # REST APIs
│
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   └── index.html
│   ├── customer/
│   │   ├── list.html
│   │   ├── add.html
│   │   └── edit.html
│   ├── service/
│   │   ├── list.html
│   │   ├── add.html
│   │   └── edit.html
│   ├── admin/
│   │   ├── login.html
│   │   └── dashboard.html
│   ├── pdf_tools/
│   │   └── index.html
│   ├── reports/
│   │   └── daily.html
│   └── errors/
│       ├── 404.html
│       ├── 403.html
│       └── 500.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── uploads/              # User uploaded files
```

### 🔐 Security Features

- ✅ CSRF Protection
- ✅ Password Hashing (Werkzeug)
- ✅ SQL Injection Prevention (SQLAlchemy ORM)
- ✅ XSS Protection (Jinja2 auto-escaping)
- ✅ Session Management
- ✅ Login Rate Limiting
- ✅ Hidden Admin Panel
- ✅ File Upload Validation

### 📊 Database Schema

**Tables:**
- operators (Cyber cafe owners)
- customers (Customer records)
- services (Service tracking)
- payments (Payment records)
- documents (Uploaded files)
- receipts (Generated receipts)
- notifications (System notifications)
- plans (Subscription plans)
- complaints (Support tickets)
- admin_logs (Admin activities)

### 🎯 Usage Guide

#### For Operators

1. **Register** at `/auth/register`
2. **Login** at `/auth/login`
3. **Add Customers** - Click "नया ग्राहक"
4. **Add Services** - Track customer requests
5. **View Reports** - Daily/Weekly/Monthly earnings
6. **Download Receipts** - Generate PDF receipts

#### For Admins

1. Visit `/secure-admin-panel-login`
2. Login with admin credentials
3. View all operators and statistics
4. Manage platform settings

### 📱 Mobile Responsive

✅ Tested on:
- iPhone (320px - 480px)
- Tablet (768px - 1024px)
- Desktop (1024px+)

### 🚀 Deployment URL

Default: `https://your-app.render.com`

### 📞 Support

For issues or questions:
- GitHub Issues: [cybercafe-erp/issues](https://github.com/pk8873/cybercafe-erp/issues)
- Email: support@example.com

### 📄 License

MIT License - Free for commercial use

### 👨‍💻 Developer

Created with ❤️ for Bihar's cyber cafe operators

---

**Version:** 1.0.0  
**Last Updated:** May 30, 2026  
**Status:** ✅ Production Ready
