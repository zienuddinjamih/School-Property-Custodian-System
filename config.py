import os

class Config:
    # Configure a strong, persistent secret using the environment variable in deployment.
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "local-demo-only-change-before-deployment")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "mysql+mysqlconnector://root:@localhost/school_property_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Set True only when the site uses HTTPS.
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "")
