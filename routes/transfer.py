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
from models.property_transfer import PropertyTransfer


transfer_bp = Blueprint(
    "transfer",
    __name__,
    url_prefix="/transfers"
)


@transfer_bp.route("/", methods=["GET", "POST"])
@login_required
def transfer_list():

    if request.method == "POST":

        property_id = request.form.get(
            "property_id",
            type=int
        )

        to_location = request.form.get(
            "to_location", ""
        ).strip()

        transfer_date_text = request.form.get(
            "transfer_date", ""
        ).strip()

        remarks = request.form.get(
            "remarks", ""
        ).strip()

        # Validate required fields
        if not property_id or not to_location:
            flash(
                "Please select a property and enter a new location.",
                "danger"
            )
            return redirect(url_for("transfer.transfer_list"))

        # Validate transfer date
        try:
            transfer_date = date.fromisoformat(
                transfer_date_text
            )
        except ValueError:
            flash(
                "Please enter a valid transfer date.",
                "danger"
            )
            return redirect(url_for("transfer.transfer_list"))

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
            return redirect(url_for("transfer.transfer_list"))

        # Prevent transferring disposed properties
        if property_item.property_status == "Disposed":
            flash(
                "Disposed properties cannot be transferred.",
                "danger"
            )
            return redirect(url_for("transfer.transfer_list"))

        from_location = (
            property_item.location or ""
        ).strip()

        # Prevent transfer to the same location
        if from_location.lower() == to_location.lower():
            flash(
                "New location must be different from the current location.",
                "danger"
            )
            return redirect(url_for("transfer.transfer_list"))

        # Record transfer history
        transfer = PropertyTransfer(
            property_id=property_item.id,
            from_location=from_location,
            to_location=to_location,
            transfer_date=transfer_date,
            transferred_by=current_user.id,
            remarks=remarks
        )

        db.session.add(transfer)

        # Update current property location
        property_item.location = to_location

        db.session.commit()

        flash(
            "Property transferred successfully!",
            "success"
        )

        return redirect(url_for("transfer.transfer_list"))

    # Display properties and transfer history
    properties = Property.query.order_by(
        Property.property_name
    ).all()

    transfers = PropertyTransfer.query.order_by(
        PropertyTransfer.transfer_date.desc(),
        PropertyTransfer.id.desc()
    ).all()

    property_lookup = {
        item.id: item
        for item in properties
    }

    return render_template(
        "transfers.html",
        properties=properties,
        transfers=transfers,
        property_lookup=property_lookup
    )
