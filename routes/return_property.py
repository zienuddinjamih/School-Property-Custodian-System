from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func

from extensions import db
from models.property import Property
from models.issuance import PropertyIssuance
from models.return_property import PropertyReturn
from models.property_condition import PropertyCondition


return_bp = Blueprint(
    "returns",
    __name__,
    url_prefix="/returns"
)


# List all property returns
@return_bp.route("/")
@login_required
def list_returns():

    returns = PropertyReturn.query.order_by(
        PropertyReturn.id.desc()
    ).all()

    return render_template(
        "returns.html",
        returns=returns
    )


# Add a new property return
@return_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_return():

    # Exclude disposed properties from the return form
    properties = Property.query.filter(
        Property.property_status != "Disposed"
    ).order_by(
        Property.property_name
    ).all()

    # Get borrowers with remaining issued quantities
    issued_records = db.session.query(
        PropertyIssuance.property_id,
        PropertyIssuance.issued_to,
        func.sum(PropertyIssuance.quantity)
    ).join(
        Property,
        Property.id == PropertyIssuance.property_id
    ).filter(
        Property.property_status != "Disposed"
    ).group_by(
        PropertyIssuance.property_id,
        PropertyIssuance.issued_to
    ).all()

    borrowers = []

    for property_id, borrower_name, total_issued in issued_records:

        total_returned = db.session.query(
            func.coalesce(
                func.sum(PropertyReturn.quantity), 0
            )
        ).filter(
            PropertyReturn.property_id == property_id,
            func.lower(PropertyReturn.returned_by) == borrower_name.lower()
        ).scalar()

        remaining = total_issued - total_returned

        if remaining > 0:
            borrowers.append(
                (property_id, borrower_name, remaining)
            )

    if request.method == "POST":

        property_id = request.form.get(
            "property_id", type=int
        )

        returned_by = request.form.get(
            "returned_by", ""
        ).strip()

        quantity = request.form.get(
            "quantity", type=int
        )

        date_text = request.form.get(
            "date_returned", ""
        )

        condition = request.form.get(
            "condition_status", ""
        )

        remarks = request.form.get(
            "remarks", ""
        ).strip()

        # Validate required fields
        if (
            not property_id
            or not returned_by
            or quantity is None
            or quantity < 1
            or not date_text
        ):
            flash(
                "Please complete all required fields.",
                "danger"
            )
            return redirect(
                url_for("returns.add_return")
            )

        # Validate property condition
        valid_conditions = [
            "Good",
            "Fair",
            "Needs Repair",
            "Damaged"
        ]

        if condition not in valid_conditions:
            flash(
                "Please select a valid property condition.",
                "danger"
            )
            return redirect(
                url_for("returns.add_return")
            )

        # Start a fresh transaction before locking
        db.session.rollback()

        # Check and lock selected property
        property_item = Property.query.filter_by(
            id=property_id
        ).with_for_update().first()

        if property_item is None:
            flash(
                "Selected property does not exist.",
                "danger"
            )
            return redirect(
                url_for("returns.add_return")
            )

        # Prevent returns for disposed properties
        if property_item.property_status == "Disposed":
            flash(
                "Disposed properties cannot be returned.",
                "danger"
            )
            return redirect(
                url_for("returns.add_return")
            )

        # Validate return date
        try:
            date_returned = datetime.strptime(
                date_text, "%Y-%m-%d"
            ).date()

        except ValueError:
            flash(
                "Invalid return date.",
                "danger"
            )
            return redirect(
                url_for("returns.add_return")
            )

        # Total issued to this borrower
        issued = db.session.query(
            func.coalesce(
                func.sum(PropertyIssuance.quantity), 0
            )
        ).filter(
            PropertyIssuance.property_id == property_id,
            func.lower(PropertyIssuance.issued_to) == returned_by.lower()
        ).scalar()

        # Total already returned by this borrower
        returned = db.session.query(
            func.coalesce(
                func.sum(PropertyReturn.quantity), 0
            )
        ).filter(
            PropertyReturn.property_id == property_id,
            func.lower(PropertyReturn.returned_by) == returned_by.lower()
        ).scalar()

        outstanding = issued - returned

        # Check borrower issuance
        if issued == 0:
            flash(
                "No issuance record found for this borrower.",
                "danger"
            )
            return redirect(
                url_for("returns.add_return")
            )

        # Prevent excessive returns
        if quantity > outstanding:
            flash(
                "Return quantity exceeds outstanding issued units.",
                "danger"
            )
            return redirect(
                url_for("returns.add_return")
            )

        # Find the matching property condition
        condition_record = PropertyCondition.query.filter_by(
            property_id=property_id,
            condition_status=condition
        ).with_for_update().first()

        # Add returned quantity to the matching condition
        if condition_record:
            condition_record.quantity += quantity

        else:
            condition_record = PropertyCondition(
                property_id=property_id,
                condition_status=condition,
                quantity=quantity
            )

            db.session.add(condition_record)

        # Save property return
        new_return = PropertyReturn(
            property_id=property_id,
            returned_by=returned_by,
            quantity=quantity,
            date_returned=date_returned,
            condition_status=condition,
            remarks=remarks,
            received_by=current_user.id
        )

        db.session.add(new_return)
        db.session.commit()

        flash(
            "Property return recorded successfully.",
            "success"
        )

        return redirect(
            url_for("returns.list_returns")
        )

    # Display the return form
    return render_template(
        "add_return.html",
        properties=properties,
        borrowers=borrowers
    )
