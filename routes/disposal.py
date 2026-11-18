
from datetime import date

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
from models.return_property import PropertyReturn
from models.property_disposal import PropertyDisposal


disposal_bp = Blueprint(
    "disposal",
    __name__,
    url_prefix="/disposals"
)


@disposal_bp.route("/", methods=["GET", "POST"])
@login_required
def disposal_list():

    if request.method == "POST":

        property_id = request.form.get(
            "property_id",
            type=int
        )

        disposal_date_text = request.form.get(
            "disposal_date", ""
        ).strip()

        reason = request.form.get(
            "reason", ""
        ).strip()

        remarks = request.form.get(
            "remarks", ""
        ).strip()

        # Validate required fields
        if not property_id or not reason:
            flash(
                "Please select a property and enter a disposal reason.",
                "danger"
            )
            return redirect(url_for("disposal.disposal_list"))

        # Validate disposal date
        try:
            disposal_date = date.fromisoformat(
                disposal_date_text
            )
        except ValueError:
            flash(
                "Please enter a valid disposal date.",
                "danger"
            )
            return redirect(url_for("disposal.disposal_list"))

        # Find selected property
        property_item = db.session.get(
            Property,
            property_id
        )

        if not property_item:
            flash(
                "Selected property was not found.",
                "danger"
            )
            return redirect(url_for("disposal.disposal_list"))

        # Prevent duplicate disposal
        if property_item.property_status == "Disposed":
            flash(
                "This property has already been disposed.",
                "danger"
            )
            return redirect(url_for("disposal.disposal_list"))

        # Calculate issued quantity
        total_issued = db.session.query(
            db.func.coalesce(
                db.func.sum(PropertyIssuance.quantity), 0
            )
        ).filter(
            PropertyIssuance.property_id == property_item.id
        ).scalar()

        # Calculate returned quantity
        total_returned = db.session.query(
            db.func.coalesce(
                db.func.sum(PropertyReturn.quantity), 0
            )
        ).filter(
            PropertyReturn.property_id == property_item.id
        ).scalar()

        outstanding = total_issued - total_returned

        # Prevent disposal of borrowed properties
        if outstanding > 0:
            flash(
                "Cannot dispose of a property with outstanding issued units.",
                "danger"
            )
            return redirect(url_for("disposal.disposal_list"))

        # Create disposal record
        disposal = PropertyDisposal(
            property_id=property_item.id,
            disposal_date=disposal_date,
            reason=reason,
            remarks=remarks,
            disposed_by=current_user.id
        )

        db.session.add(disposal)

        # Update property status
        property_item.property_status = "Disposed"

        db.session.commit()

        flash(
            "Property disposed successfully!",
            "success"
        )

        return redirect(url_for("disposal.disposal_list"))

    # Display property records
    properties = Property.query.order_by(
        Property.property_name
    ).all()

    disposals = PropertyDisposal.query.order_by(
        PropertyDisposal.disposal_date.desc(),
        PropertyDisposal.id.desc()
    ).all()

    property_lookup = {
        item.id: item
        for item in properties
    }

    return render_template(
        "disposals.html",
        properties=properties,
        disposals=disposals,
        property_lookup=property_lookup
    )
