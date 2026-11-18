School Property System - 13 Required Features Update (2026-11-17)

WHAT WAS ADDED
- Original SVG school/property logo, consistent navy branding, favicon across HTML pages.
- My Profile page at /profile: change name/email/password after verifying current password.
- SMTP registration-confirmation email helper (sends only after MAIL_* environment settings are supplied).
- Configurable Flask secret key, database URL, secure cookie settings, 8-character registration password minimum.
- Existing inventory, issuance, return, transfer, disposal, reports and database models retained.

IMPORTANT: EMAIL IS NOT VERIFIED UNTIL YOU CONFIGURE AND TEST REAL SMTP.
MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD and MAIL_DEFAULT_SENDER
must be set as environment variables. The app still allows registration if SMTP is unconfigured
or unavailable, but no email will be delivered. Never commit or share actual SMTP passwords.

WINDOWS POWERSHELL EXAMPLE (same terminal before `py app.py`):
$env:FLASK_SECRET_KEY='replace-with-long-random-string'
$env:MAIL_SERVER='smtp.yourprovider.com'
$env:MAIL_PORT='587'
$env:MAIL_USE_TLS='true'
$env:MAIL_USERNAME='your-account@example.com'
$env:MAIL_PASSWORD='your-provider-app-password'
$env:MAIL_DEFAULT_SENDER='your-account@example.com'

INSTALL: Make a copy of your original project, then extract this ZIP into a NEW folder.
Use the same local MySQL database school_property_db; no schema migration needed.
The venv folder is intentionally excluded; use your existing venv or pip install -r requirements.txt.
Set FLASK_SECRET_KEY to a long secret; changing the key signs users out.
Start MySQL, then `py app.py` in the new project directory.

TEST PLAN
1. Home/Login/Register logo and favicon; registration and invalid credentials.
2. Login, dashboard, My Profile: update name/email, wrong password, change password, log back in.
3. Verify login-required routes redirect after logout.
4. Add, edit, search, filter and delete a NEW test property with no transactions.
5. Issue and return test units; verify counts and condition validations.
6. Transfer test property; check transfer history.
7. Dispose of an eligible test property; verify edit/delete/issue/return blocked.
8. Check inventory, issuance and return reports and printing.
9. Test phone-size layout and menu scrolling.
10. Configure SMTP, register with a real test inbox and confirm email receipt.

KNOWN LIMITATIONS / SAFETY
- This is a LOCAL DEMO application, not hardened for internet-facing production use.
- SMTP delivery is untested without credentials/network access.
- Bootstrap currently loads from a CDN, so styling may require internet access.
- User model and SQLAlchemy ORM provide OOP classes; further OOP design can be expanded.
- Logout uses the existing GET endpoint; for a production system use a CSRF-protected POST logout.
- Review every form and edge case manually; static compilation is not a full runtime test.
- Do NOT include config secrets, email passwords, or private user data when sharing this ZIP.
