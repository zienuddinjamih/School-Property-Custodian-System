# School Property Custodian – Inventory and Management System

A web-based school property inventory and management system built with Python Flask, MySQL, HTML, CSS, Bootstrap, and JavaScript. It supports user accounts, property records, inventory conditions, issuances, returns, transfers, disposals, and reports.

## Requirements

- Python 3
- MySQL (for example, through XAMPP)
- Git (optional, for cloning)
- Python packages in `requirements.txt`

## Set up locally (Windows PowerShell)

1. Download or clone the repository and open its folder:

   ```powershell
   git clone https://github.com/zienuddinjamih/School-Property-Custodian-System.git
   cd School-Property-Custodian-System
   ```

2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

   The application imports `python-dotenv`; if that package is not already listed in `requirements.txt`, also run `pip install python-dotenv`.

4. Start **MySQL** in the XAMPP Control Panel. Open `http://localhost/phpmyadmin` and create a database named **`school_property_db`** (or use a different name and update the connection string below).

5. Create a **`.env`** file in the project root using `.env.example` as a guide. For a local XAMPP installation with the default MySQL `root` account and no password:

   ```dotenv
   FLASK_SECRET_KEY=replace-with-a-long-random-secret
   DATABASE_URL=mysql+mysqlconnector://root:@localhost/school_property_db
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=
   MAIL_PASSWORD=
   MAIL_DEFAULT_SENDER=
   SESSION_COOKIE_SECURE=false
   ```

   Adjust `DATABASE_URL` to match your local MySQL credentials. SMTP settings are optional for basic local testing; registration emails require valid mail credentials. **Never commit `.env`, passwords, or other secrets.**

6. Run the application:

   ```powershell
   python app.py
   ```

   Open **http://127.0.0.1:5000/** in a browser. Register an account and log in to use the dashboard.

## Database initialization

The application calls `db.create_all()` when it starts, which creates missing tables in the configured MySQL database. **Create the database itself first** in phpMyAdmin. `db.create_all()` does not migrate existing tables, import sample data, or restore previous records. A fresh installation starts with an empty inventory.

## Main functions

- Public home page, registration, login, and profile management
- Property inventory management and condition tracking
- Property issuance and return records
- Property transfers and disposals
- Inventory dashboard and reports

## Notes

This configuration is intended for **local development and demonstration**, not public production deployment. The `.env` file and `.venv` folder should remain outside Git version control.
