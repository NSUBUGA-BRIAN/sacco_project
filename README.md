# SACCO Loan Management System — Setup Guide

## What Was Built
A complete Django-based SACCO Loan Management System with:
- Custom user model (Member + Admin roles)
- Full loan workflow: Draft → Submitted → Under Review → Approved → Disbursed → Completed
- Automatic repayment schedule generation
- Admin dashboard with charts
- Member portal
- REST API endpoints
- Notification system
- Reports & analytics
- Professional fintech UI

---

## Project Structure

```
sacco_project/                  ← Your project root
│
├── manage.py
├── requirements.txt
│
├── sacco_core/                 ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                   ← User auth + member management
│   ├── models.py               (Custom User model)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── serializers.py
│   ├── api_urls.py
│   ├── api_views.py
│   └── management/commands/
│       └── seed_demo_data.py   ← Demo data seeder
│
├── loans/                      ← Core loan module
│   ├── models.py               (Loan, LoanType, LoanAuditLog)
│   ├── views.py
│   ├── forms.py
│   ├── services.py             ← Business logic layer
│   ├── urls.py
│   └── api_*.py
│
├── repayments/                 ← Repayment tracking
│   ├── models.py               (Repayment)
│   ├── views.py
│   ├── services.py             ← Schedule generation
│   └── urls.py
│
├── notifications/              ← In-app notifications
│   ├── models.py
│   ├── services.py
│   └── context_processors.py
│
├── dashboard/                  ← Member + Admin dashboards
│   └── views.py
│
├── reports/                    ← Analytics & reports
│   └── views.py
│
└── templates/                  ← All HTML templates
    ├── base.html               ← Sidebar + topbar layout
    ├── accounts/
    │   ├── login.html
    │   ├── register.html
    │   ├── profile.html
    │   ├── member_list.html
    │   └── member_detail.html
    ├── dashboard/
    │   ├── admin_dashboard.html
    │   └── member_dashboard.html
    ├── loans/
    │   ├── loan_list.html
    │   ├── loan_apply.html
    │   └── loan_detail.html
    ├── repayments/
    │   ├── repayment_list.html
    │   ├── loan_repayments.html
    │   └── record_payment.html
    ├── reports/
    │   └── reports.html
    └── notifications/
        └── notification_list.html
```

---

## Step-by-Step Setup in Your VS Code

### Step 1 — Copy the project files
Copy the entire `sacco_project/` folder into your VS Code workspace.

### Step 2 — Activate your virtual environment
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

If `python-dateutil` is not included, also run:
```bash
pip install python-dateutil
```

### Step 4 — Run migrations
```bash
python manage.py makemigrations accounts loans repayments notifications
python manage.py migrate
```

### Step 5 — Seed demo data
```bash
python manage.py seed_demo_data
```
This creates admin and member accounts plus sample loans.

### Step 6 — Run the server
```bash
python manage.py runserver
```

### Step 7 — Open in browser
Go to: **http://127.0.0.1:8000**

---

## Login Credentials

| Role      | Username  | Password   |
|-----------|-----------|------------|
| Admin     | admin     | admin123   |
| Member 1  | member1   | member123  |
| Member 2  | member2   | member123  |
| Member 3  | member3   | member123  |

---

## Key URLs

| Page                | URL                          |
|---------------------|------------------------------|
| Login               | /accounts/login/             |
| Register            | /accounts/register/          |
| Dashboard           | /dashboard/                  |
| Loans               | /loans/                      |
| Apply for Loan      | /loans/apply/                |
| Repayments          | /repayments/                 |
| Reports (admin)     | /reports/                    |
| Notifications       | /notifications/              |
| Django Admin        | /admin/                      |
| API - Users         | /api/users/                  |
| API - Loans         | /api/loans/                  |
| API - Repayments    | /api/repayments/             |

---

## Switching to PostgreSQL

1. Create a `.env` file in the project root:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=sacco_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key-here
DEBUG=True
```

2. Create the database:
```sql
CREATE DATABASE sacco_db;
```

3. Re-run migrations:
```bash
python manage.py migrate
python manage.py seed_demo_data
```

---

## Business Rules Enforced

- Members cannot apply if they have an overdue payment
- Members cannot have two active pending applications
- Loan maximum = 3× monthly income
- Workflow strictly enforced: Draft → Submit → Review → Approve/Reject → Disburse → Complete
- Only admins can approve, reject, or disburse loans
- Completed/Rejected loans cannot be edited

---

## Deployment Checklist (Render/Railway)

1. Set `DEBUG=False` in production
2. Set a strong `SECRET_KEY`
3. Add your domain to `ALLOWED_HOSTS`
4. Use PostgreSQL in production
5. Run `python manage.py collectstatic`
6. Use Gunicorn: `gunicorn sacco_core.wsgi`
