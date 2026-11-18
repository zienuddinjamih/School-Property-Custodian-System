from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from extensions import db
from models.property import Property
from models.issuance import PropertyIssuance
from models.property_condition import PropertyCondition


issuance_bp = Blueprint(
    "issuance",
    __name__,
    url_prefix="/issuances"
)


# VIEW ISSUANCE RECORDS
@issuance_bp.route("/")
@login_required
def list_issuances():

    issuances = PropertyIssuance.query.order_by(
        PropertyIssuance.id.desc()
    ).all()

    return render_template(
        "issuances.html",
        issuances=issuances
    )


# ADD NEW ISSUANCE
@issuance_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_issuance():

    # Do not show disposed properties in the issuance form
    properties = Property.query.filter(
        Property.property_status != "Disposed"
    ).order_by(
        Property.property_name
    ).all()

    if request.method == "POST":

        property_id = request.form.get("property_id", "")
        issued_to = request.form.get("issued_to", "").strip()
        position = request.form.get("position", "").strip()
        office_room = request.form.get("office_room", "").strip()
        date_issued = request.form.get("date_issued", "")
        condition = request.form.get("condition_status", "")
        remarks = request.form.get("remarks", "").strip()
        quantity = request.form.get("quantity", "")

        # Validate required information
        if not property_id or not issued_to or not date_issued:
            flash("Please complete all required fields.", "danger")
            return redirect(url_for("issuance.add_issuance"))

        try:
            property_id = int(property_id)
            quantity = int(quantity)

            issued_date = datetime.strptime(
                date_issued, "%Y-%m-%d"
            ).date()

            if quantity < 1:
                raise ValueError

        except ValueError:
            flash("Invalid property, quantity, or date.", "danger")
            return redirect(url_for("issuance.add_issuance"))

        # Find selected property
        property = db.session.get(Property, property_id)

        if not property:
            flash("Property not found.", "danger")
            return redirect(url_for("issuance.add_issuance"))

        # Prevent issuing disposed properties, including direct POST requests
        if property.property_status == "Disposed":
            flash("Disposed properties cannot be issued.", "danger")
            return redirect(url_for("issuance.add_issuance"))

        # Allow only serviceable conditions
        if condition not in ["Good", "Fair"]:
            flash(
                "Only Good and Fair condition units can be issued.",
                "danger"
            )
            return redirect(url_for("issuance.add_issuance"))

        # Find available units by condition
        condition_record = PropertyCondition.query.filter_by(
            property_id=property_id,
            condition_status=condition
        ).with_for_update().first()

        available = (
            condition_record.quantity
            if condition_record else 0
        )

        # Prevent issuing more than available
        if quantity > available:
            flash(
                f"Only {available} unit(s) in {condition} "
                "condition are available.",
                "danger"
            )
            return redirect(url_for("issuance.add_issuance"))

        # Save issuance
        new_issuance = PropertyIssuance(
            property_id=property_id,
            issued_to=issued_to,
            position=position,
            office_room=office_room,
            date_issued=issued_date,
            condition_status=condition,
            remarks=remarks,
            issued_by=current_user.id,
            quantity=quantity
        )

        # Deduct issued units from available condition
        condition_record.quantity -= quantity

        # Update property status
        property.property_status = "In Use"

        # Save changes
        db.session.add(new_issuance)
        db.session.commit()

        flash("Property issued successfully.", "success")

        return redirect(
            url_for("issuance.list_issuances")
        )

    # Get condition quantities for each property
    condition_data = {}

    for property_item in properties:

        condition_records = PropertyCondition.query.filter_by(
            property_id=property_item.id
        ).all()

        condition_data[property_item.id] = {
            item.condition_status: item.quantity
            for item in condition_records
        }

    return render_template(
        "add_issuance.html",
        properties=properties,
        condition_data=condition_data
    )
