"""SMTP notification helper. Set MAIL_* environment variables to enable sending."""
import smtplib
import ssl
from email.message import EmailMessage
from flask import current_app


def send_registration_email(recipient, full_name):
    cfg = current_app.config
    if not all(cfg.get(k) for k in ("MAIL_SERVER", "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_DEFAULT_SENDER")):
        current_app.logger.info("SMTP not configured; registration email skipped")
        return False
    message = EmailMessage()
    message["Subject"] = "School Property System - Registration Confirmation"
    message["From"] = cfg["MAIL_DEFAULT_SENDER"]
    message["To"] = recipient
    message.set_content(
        f"Hello {full_name},\n\nYour School Property System account was created successfully.\n"
        "You can now sign in to your account.\n\nSchool Property System"
    )
    context = ssl.create_default_context()
    try:
        if cfg["MAIL_USE_TLS"]:
            with smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=12) as server:
                server.starttls(context=context)
                server.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
                server.send_message(message)
        else:
            with smtplib.SMTP_SSL(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], context=context, timeout=12) as server:
                server.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
                server.send_message(message)
    except (smtplib.SMTPException, OSError) as exc:
        current_app.logger.warning("Registration email could not be sent: %s", type(exc).__name__)
        return False
    return True
