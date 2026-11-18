from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template
from flask_login import login_required

from config import Config

from extensions import (
    db,
    login_manager,
    csrf
)


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Login settings
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please login first."
    
# Import models
    from models.user import User
    from models.property import Property
    from models.issuance import PropertyIssuance
    from models.return_property import PropertyReturn
    from models.property_condition import PropertyCondition
    from models.property_transfer import PropertyTransfer
    from models.property_disposal import PropertyDisposal

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register authentication routes
    from routes.auth import auth
    app.register_blueprint(auth)

    # Register property routes
    from routes.property import property_bp
    app.register_blueprint(property_bp)

    from routes.issuance import issuance_bp
    app.register_blueprint(issuance_bp)

    from routes.return_property import return_bp
    app.register_blueprint(return_bp)

    from routes.reports import reports_bp
    app.register_blueprint(reports_bp)
    
    # Register property transfer routes
    from routes.transfer import transfer_bp
    app.register_blueprint(transfer_bp)

    # Register property disposal routes
    from routes.disposal import disposal_bp
    app.register_blueprint(disposal_bp)
    
    # HOME PAGE
    @app.route("/")
    def home():
        return render_template("index.html")

    # DASHBOARD PAGE
    @app.route("/dashboard")
    @login_required
    def dashboard():

        # Count property records
        total_properties = Property.query.count()

        # Get active properties
        properties = Property.query.filter(
            Property.property_status != "Disposed"
        ).all()

        # Initialize inventory quantities
        total_quantity = 0
        good = 0
        fair = 0
        under_repair = 0
        damaged = 0
        in_use = 0

        for property_item in properties:

            total_quantity += property_item.quantity

            # Get condition quantities
            condition_records = PropertyCondition.query.filter_by(
                property_id=property_item.id
            ).all()

            for record in condition_records:

                if record.condition_status == "Good":
                    good += record.quantity

                elif record.condition_status == "Fair":
                    fair += record.quantity

                elif record.condition_status == "Needs Repair":
                    under_repair += record.quantity

                elif record.condition_status == "Damaged":
                    damaged += record.quantity

            # Count issued units
            total_issued = db.session.query(
                db.func.coalesce(
                    db.func.sum(PropertyIssuance.quantity), 0
                )
            ).filter(
                PropertyIssuance.property_id == property_item.id
            ).scalar()

            # Count returned units
            total_returned = db.session.query(
                db.func.coalesce(
                    db.func.sum(PropertyReturn.quantity), 0
                )
            ).filter(
                PropertyReturn.property_id == property_item.id
            ).scalar()

            # Calculate outstanding issued units
            in_use += total_issued - total_returned

        # Calculate available serviceable units
        available = good + fair

        return render_template(
            "dashboard.html",
            total_properties=total_properties,
            total_quantity=total_quantity,
            available=available,
            in_use=in_use,
            good=good,
            fair=fair,
            under_repair=under_repair,
            damaged=damaged
        )

    # Return Flask application
    return app


# Create Flask application
app = create_app()

# Create missing database tables
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
