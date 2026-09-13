# 💊 MediTrack – Smart Medical Expiry and Inventory Management System

MediTrack is a full-stack Pharmacy Management System built with **Django 5**,
**MySQL 8**, **Bootstrap 5**, and vanilla **JavaScript**. Its centerpiece is
the **Smart Medicine Expiry Alert Center**, which calculates expiry &amp; stock
status *live* from the current date — nothing is ever stored or goes stale.

---

## ✨ Features / Modules

1. **Login Authentication** – single admin account, email-based login, no public registration.
2. **Dashboard** – live KPIs, notification bell, recent activity feed, quick actions, Chart.js charts.
3. **Medicine Management** – full CRUD, image upload, search, filter, pagination.
4. **Inventory Management** – real-time stock levels, colored status badges.
5. **Smart Medicine Expiry Alert Center** – expired / today / tomorrow / 7 days / 30 days / safe, calculated dynamically.
6. **Customer Management** – CRUD + purchase history.
7. **Supplier Management** – CRUD + linked medicines.
8. **Billing** – cart-style invoice builder, live medicine search, GST & discount calculation, stock auto-deduction, blocks expired medicines, printable invoice.
9. **Settings** – admin profile editing & change password.

---

## 🧰 Technology Stack

| Layer       | Technology                                   |
|-------------|-----------------------------------------------|
| Backend     | Python 3.10+, Django 5.x                      |
| Frontend    | HTML5, CSS3, Bootstrap 5, JavaScript, Font Awesome, Google Fonts (Poppins) |
| Database    | MySQL 8.x                                     |
| Charts      | Chart.js                                      |
| Editor      | Visual Studio Code                            |

---

## 📁 Project Structure

```
meditrack/
├── manage.py
├── requirements.txt
├── db.sql                     # Reference MySQL schema
├── README.md
├── meditrack/                 # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
├── accounts/                  # Authentication & Settings
│   ├── views.py / forms.py / urls.py
│   └── management/commands/seed_admin.py
├── core/                      # Main pharmacy application
│   ├── models.py              # Category, Supplier, Customer, Medicine, Bill, BillItem, ActivityLog
│   ├── views.py / forms.py / urls.py / admin.py
│   ├── context_processors.py  # Notification bell data
│   ├── templatetags/core_extras.py
│   └── migrations/
├── templates/
│   ├── base.html
│   ├── accounts/  dashboard/  medicines/  inventory/  expiry/
│   ├── customers/  suppliers/  billing/  partials/
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   └── images/
└── media/
    └── medicines/              # Uploaded medicine images
```

---

## 🚀 Installation Guide

### 1. Prerequisites
- Python 3.10 or higher
- MySQL Server 8.x (running locally or remotely)
- pip / virtualenv
- Visual Studio Code (recommended)

### 2. Clone / Extract the Project
Extract the ZIP file and open the `meditrack/` folder in VS Code.

### 3. Create & Activate a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```
> `mysqlclient` requires MySQL's development headers to build. If installation
> fails on Windows, install the prebuilt wheel matching your Python version,
> or use `pip install mysqlclient --only-binary :all:`.
> On macOS: `brew install mysql-client pkg-config` before installing.
> On Ubuntu/Debian: `sudo apt install default-libmysqlclient-dev build-essential pkg-config`.

### 5. Configure MySQL

Log into MySQL and create the database:
```sql
CREATE DATABASE meditrack_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Set your database credentials as environment variables (or edit the
defaults directly in `meditrack/settings.py`):

```bash
# Windows (cmd)
set DB_NAME=meditrack_db
set DB_USER=root
set DB_PASSWORD=yourpassword
set DB_HOST=127.0.0.1
set DB_PORT=3306

# macOS / Linux
export DB_NAME=meditrack_db
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_HOST=127.0.0.1
export DB_PORT=3306
```

> 💡 **Quick local testing without MySQL:** `meditrack/settings.py` contains a
> commented-out SQLite configuration you can temporarily enable if you just
> want to try the app without setting up MySQL first.

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create the Default Admin Account
MediTrack ships with a management command that provisions the **single**
admin account required by the project spec (no registration page exists):
```bash
python manage.py seed_admin
```

**Default Login Credentials**
| Field    | Value                          |
|----------|---------------------------------|
| Email    | `24sbca088@psgrkcw.ac.in`       |
| Password | `saikishori@123`                |

You can change the password anytime from **Settings → Change Password**
once logged in.

### 8. Collect Static Files (optional, for production)
```bash
python manage.py collectstatic
```

### 9. Run the Development Server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your browser — you'll be redirected to
the login page automatically.

---

## 🔐 Security Notes
- Django's built-in authentication system with hashed (PBKDF2) passwords.
- CSRF protection enabled on every form (`{% csrf_token %}`).
- `@login_required` guards every view except the login page.
- Session-based auth with `LOGIN_URL` redirect for unauthenticated access.
- Server-side form validation on all Create/Update forms.
- Expired medicines are blocked from billing at the view layer, not just the UI.

---

## 🧪 Quick Smoke Test Checklist
1. Log in with the default credentials above.
2. Add a **Category** and a **Supplier** (via the Supplier module).
3. Add a **Medicine** with an expiry date within the next 5 days.
4. Open **Expiry Alert Center** → confirm it appears under "Within 7 Days".
5. Go to **Billing → Create Bill**, search the medicine, add it to the cart, and generate an invoice.
6. Confirm the medicine's stock quantity decreased on the **Inventory** page.
7. Try billing an **expired** medicine — the system should reject it.

---

## 📌 Notes on the Smart Expiry Logic
Expiry and stock status are **never persisted** to the database. Every time a
page is rendered, MediTrack recalculates:
- `days_to_expiry = expiry_date - today`
- Status buckets: `expired`, `expiring_today`, `expiring_tomorrow`,
  `expiring_week` (≤7 days), `expiring_month` (≤30 days), `safe`
- Stock buckets: `out_of_stock`, `low_stock` (≤ minimum_stock), `in_stock`

This guarantees the alert center is always accurate with zero background
jobs, cron tasks, or stale cached fields.

---

## 👩‍💻 Author / Academic Use
Developed as an internship-level Django project demonstrating full-stack
CRUD, authentication, dynamic business logic, and a polished healthcare UI.
