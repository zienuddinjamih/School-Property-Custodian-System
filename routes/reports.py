
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from models.user import User

from models.property import Property
from models.issuance import PropertyIssuance
from models.return_property import PropertyReturn
from models.property_condition import PropertyCondition

from sqlalchemy import func
from extensions import db


reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


@reports_bp.route("/")
@login_required
def reports_home():

    total_properties = Property.query.count()
    total_issuances = PropertyIssuance.query.count()
    total_returns = PropertyReturn.query.count()

    return render_template(
        "reports.html",
        total_properties=total_properties,
        total_issuances=total_issuances,
        total_returns=total_returns
    )

# Property Inventory Report
@reports_bp.route("/inventory")
@login_required
def inventory_report():

        # Get selected dates
    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")

    # Validate date range
    if from_date and to_date:
        if from_date > to_date:
            flash(
                "Invalid Date Range! From Date must not be later than To Date.",
                "danger"
            )

            return redirect(
                url_for("reports.inventory_report")
            )

    # Start with all properties
    query = Property.query

    # Filter by Date Acquired
    if from_date:
        query = query.filter(
            Property.date_acquired >= from_date
        )

    if to_date:
        query = query.filter(
            Property.date_acquired <= to_date
        )

    # Get filtered properties
    properties = query.order_by(
        Property.property_name
    ).all()

    inventory = []

    for property_item in properties:

        # Initialize condition quantities
        conditions = {
            "Good": 0,
            "Fair": 0,
            "Needs Repair": 0,
            "Damaged": 0
        }

        # Get condition records
        condition_records = PropertyCondition.query.filter_by(
            property_id=property_item.id
        ).all()

        for record in condition_records:

            if record.condition_status in conditions:

                conditions[record.condition_status] += record.quantity

        # Total issued quantity
        total_issued = db.session.query(
            func.coalesce(
                func.sum(PropertyIssuance.quantity), 0
            )
        ).filter(
            PropertyIssuance.property_id == property_item.id
        ).scalar()

        # Total returned quantity
        total_returned = db.session.query(
            func.coalesce(
                func.sum(PropertyReturn.quantity), 0
            )
        ).filter(
            PropertyReturn.property_id == property_item.id
        ).scalar()

        # Calculate outstanding issued units
        in_use = total_issued - total_returned

        # Calculate available serviceable units
        available = conditions["Good"] + conditions["Fair"]

        # Determine current property status
        if property_item.property_status == "Disposed":
            current_status = "Disposed"
            available = 0

        elif in_use > 0:
            current_status = "In Use"

        elif available > 0:
            current_status = "Available"

        else:
            current_status = "Under Repair"

        # Prepare inventory report data
        inventory.append({
            "property": property_item,
            "total": property_item.quantity,
            "available": available,
            "in_use": in_use,
            "conditions": conditions,
            "status": current_status
        })

    return render_template(
        "inventory_report.html",
        inventory=inventory,
        from_date=from_date,
        to_date=to_date
    )

# Property Issuance Report with Date Filter
@reports_bp.route("/issuances")
@login_required
def issuance_report():

    # Get selected dates
    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")

    # Validate date range
    if from_date and to_date:

        if from_date > to_date:

            flash(
                "Invalid Date Range! From Date must not be later than To Date.",
                "danger"
            )

            return redirect(
                url_for("reports.issuance_report")
            )

    # Get all issuance records
    query = PropertyIssuance.query

    # Filter starting date
    if from_date:
        query = query.filter(
            PropertyIssuance.date_issued >= from_date
        )

    # Filter ending date
    if to_date:
        query = query.filter(
            PropertyIssuance.date_issued <= to_date
        )

    # Sort newest first
    issuances = query.order_by(
        PropertyIssuance.date_issued.desc()
    ).all()

    # Get property information
    properties = Property.query.all()

    # Create property lookup dictionary
    property_lookup = {
        item.id: item for item in properties
    }

    # Calculate issuance summary
    total_transactions = len(issuances)

    total_issued_quantity = sum(
        item.quantity for item in issuances
    )

    # Calculate issued quantities by condition
    total_good = sum(
        item.quantity for item in issuances
        if item.condition_status == "Good"
    )

    total_fair = sum(
        item.quantity for item in issuances
        if item.condition_status == "Fair"
    )

    return render_template(
        "issuance_report.html",
        issuances=issuances,
        from_date=from_date,
        to_date=to_date,
        total_transactions=total_transactions,
        total_issued_quantity=total_issued_quantity,
        total_good=total_good,
        total_fair=total_fair,
        property_lookup=property_lookup
    )


# Property Return Report with Date Filter
@reports_bp.route("/returns")
@login_required
def return_report():

    # Get selected dates
    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")

    # Validate date range
    if from_date and to_date:
        if from_date > to_date:
            flash(
                "Invalid Date Range! From Date must not be later than To Date.",
                "danger"
            )
            return redirect(
                url_for("reports.return_report")
            )

    # Get return records
    query = PropertyReturn.query

    if from_date:
        query = query.filter(
            PropertyReturn.date_returned >= from_date
        )

    if to_date:
        query = query.filter(
            PropertyReturn.date_returned <= to_date
        )

    returns = query.order_by(
        PropertyReturn.date_returned.desc(),
        PropertyReturn.id.desc()
    ).all()

    # Get property information
    properties = Property.query.all()

    property_lookup = {
        item.id: item for item in properties
    }
    # Get receiving personnel information
    users = User.query.all()

    user_lookup = {
        user.id: user.full_name
        for user in users
    }
    # Calculate report summary
    total_transactions = len(returns)

    total_returned_quantity = sum(
        item.quantity for item in returns
    )

    total_good = sum(
        item.quantity for item in returns
        if item.condition_status == "Good"
    )

    total_fair = sum(
        item.quantity for item in returns
        if item.condition_status == "Fair"
    )

    total_needs_repair = sum(
        item.quantity for item in returns
        if item.condition_status == "Needs Repair"
    )

    total_damaged = sum(
        item.quantity for item in returns
        if item.condition_status == "Damaged"
    )

    return render_template(
        "return_report.html",
        returns=returns,
        from_date=from_date,
        to_date=to_date,
        property_lookup=property_lookup,
        total_transactions=total_transactions,
        total_returned_quantity=total_returned_quantity,
        total_good=total_good,
        total_fair=total_fair,
        total_needs_repair=total_needs_repair,
        total_damaged=total_damaged,
        user_lookup=user_lookup
    )




