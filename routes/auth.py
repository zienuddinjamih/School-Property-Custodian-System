from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from models.user import User
from extensions import db
from services.email_service import send_registration_email


auth = Blueprint(
    "auth",
    __name__
)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower().lower()
        password = request.form.get("password")
        confirm_password = request.form.get(
            "confirm_password"
        )

        if not full_name or not email or not password:

            flash(
                "Please complete all required fields.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email is already registered.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        new_user = User(
            full_name=full_name,
            email=email,
            role="Staff"
        )

        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        send_registration_email(new_user.email, new_user.full_name)

        flash(
            "Registration successful. You can now login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html"
    )


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.check_password(password):

                login_user(user)

                return redirect(
                    url_for("dashboard")
                )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html"
    )


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )

@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not full_name or not email or "@" not in email:
            flash("Please provide a valid name and email.", "danger")
            return redirect(url_for("auth.profile"))
        if len(full_name) > 100 or len(email) > 100:
            flash("Name or email is too long.", "danger")
            return redirect(url_for("auth.profile"))
        existing = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing:
            flash("Email is already registered.", "danger")
            return redirect(url_for("auth.profile"))
        # Password required for any account update, not just password changes.
        if not current_user.check_password(current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("auth.profile"))
        if new_password:
            if len(new_password) < 8:
                flash("New password must be at least 8 characters.", "danger")
                return redirect(url_for("auth.profile"))
            if new_password != confirm_password:
                flash("New passwords do not match.", "danger")
                return redirect(url_for("auth.profile"))
            current_user.set_password(new_password)
        current_user.full_name = full_name
        current_user.email = email
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.profile"))
    return render_template("profile.html")
