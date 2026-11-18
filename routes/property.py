
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from sqlalchemy import text
from flask_login import login_required
from datetime import datetime

from extensions import db
from models.property import Property
from models.property_condition import PropertyCondition
from models.issuance import PropertyIssuance
from models.return_property import PropertyReturn

property_bp = Blueprint(
    "property",
    __name__,
    url_prefix="/properties"
)


# VIEW PROPERTIES
@property_bp.route("/")
@login_required
def list_properties():

    # Get search and filter values
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    status = request.args.get("status", "").strip()

    # Start property query
    query = Property.query

    # Search by property code or name
    if search:
        query = query.filter(
            db.or_(
                Property.property_code.ilike(f"%{search}%"),
                Property.property_name.ilike(f"%{search}%")
            )
        )

    # Get categories from MySQL
    categories = db.session.execute(
        text(
            "SELECT id, category_name FROM categories "
            "ORDER BY category_name"
        )
    ).mappings().all()

    # Filter by category
    if category:
        try:
            category_id = int(category)
            valid_ids = {item["id"] for item in categories}

            if category_id in valid_ids:
                query = query.filter(
                    Property.category_id == category_id
                )
            else:
                query = query.filter(Property.id == -1)

        except ValueError:
            query = query.filter(Property.id == -1)

    # Get filtered properties
    properties = query.order_by(
        Property.id.desc()
    ).all()

    
    # Match category IDs with names
    category_names = {
        item["id"]: item["category_name"]
        for item in categories
    }

    # Prepare inventory information
    inventory_data = {}

    for property_item in properties:

        # Default condition quantities
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
            conditions[record.condition_status] = record.quantity

        # Count total issued units
        total_issued = db.session.query(
            db.func.coalesce(
                db.func.sum(PropertyIssuance.quantity), 0
            )
        ).filter(
            PropertyIssuance.property_id == property_item.id
        ).scalar()

        # Count total returned units
        total_returned = db.session.query(
            db.func.coalesce(
                db.func.sum(PropertyReturn.quantity), 0
            )
        ).filter(
            PropertyReturn.property_id == property_item.id
        ).scalar()

        # Calculate inventory quantities
        available = conditions["Good"] + conditions["Fair"]
        in_use = total_issued - total_returned

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

        # Store inventory information
        inventory_data[property_item.id] = {
            "total": property_item.quantity,
            "available": available,
            "in_use": in_use,
            "conditions": conditions,
            "status": current_status
        }

    # Filter using calculated inventory status
    if status:
        properties = [
            property_item
            for property_item in properties
            if inventory_data[property_item.id]["status"] == status
        ]

    return render_template(
        "properties.html",
        properties=properties,
        category_names=category_names,
        categories=categories,
        search=search,
        selected_category=category,
        selected_status=status,
        inventory_data=inventory_data
    )

# ADD PROPERTY
@property_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_property():

    # Load categories from MySQL
    categories = db.session.execute(
        text(
            "SELECT id, category_name FROM categories "
            "ORDER BY category_name"
        )
    ).mappings().all()

    if request.method == "POST":

        property_code = request.form.get(
            "property_code", ""
        ).strip()

        property_name = request.form.get(
            "property_name", ""
        ).strip()

        category = request.form.get("category", "")
        quantity = request.form.get("quantity", "1")
        condition = request.form.get("condition", "Good")
        location = request.form.get("location", "").strip()
        date_acquired = request.form.get("date_acquired", "")

        # Valid property conditions
        valid_conditions = [
            "Good",
            "Fair",
            "Needs Repair",
            "Damaged"
        ]

        # Check required fields
        if not property_code or not property_name:
            flash(
                "Please complete all required fields.",
                "danger"
            )
            return redirect(
                url_for("property.add_property")
            )

        # Validate condition
        if condition not in valid_conditions:
            flash("Invalid property condition.", "danger")
            return redirect(
                url_for("property.add_property")
            )

        # Check duplicate property code
        existing_property = Property.query.filter_by(
            property_code=property_code
        ).first()

        if existing_property:
            flash("Property code already exists.", "danger")
            return redirect(
                url_for("property.add_property")
            )

        # Validate quantity, category, and date
        try:
            quantity = int(quantity)
            category_id = int(category)

            if quantity < 1:
                raise ValueError

            valid_category_ids = {
                item["id"] for item in categories
            }

            if category_id not in valid_category_ids:
                raise ValueError

            date_acquired = (
                datetime.strptime(
                    date_acquired, "%Y-%m-%d"
                ).date()
                if date_acquired else None
            )

        except ValueError:
            flash(
                "Invalid quantity, category, or date.",
                "danger"
            )
            return redirect(
                url_for("property.add_property")
            )

        # Automatically determine initial status
        if condition in ["Good", "Fair"]:
            status = "Available"
        else:
            status = "Under Repair"

        # Create new property
        new_property = Property(
            property_code=property_code,
            property_name=property_name,
            category_id=category_id,
            quantity=quantity,
            condition_status=condition,
            location=location,
            date_acquired=date_acquired,
            property_status=status
        )

        db.session.add(new_property)

        # Generate property ID before committing
        db.session.flush()

        # Create initial condition records
        for item in valid_conditions:

            condition_record = PropertyCondition(
                property_id=new_property.id,
                condition_status=item,
                quantity=quantity if item == condition else 0
            )

            db.session.add(condition_record)

        # Save property and condition records
        db.session.commit()

        flash(
            "Property added successfully.",
            "success"
        )

        return redirect(
            url_for("property.list_properties")
        )

    return render_template(
        "add_property.html",
        categories=categories
    )


# EDIT PROPERTY
@property_bp.route("/edit/<int:property_id>", methods=["GET", "POST"])
@login_required
def edit_property(property_id):

    # Find selected property
    property = db.get_or_404(Property, property_id)

    # Prevent editing disposed properties
    if property.property_status == "Disposed":

        flash(
            "Disposed properties cannot be edited.",
            "danger"
        )

        return redirect(
            url_for("property.list_properties")
        )

    # Load categories
    categories = db.session.execute(
        text(
            "SELECT id, category_name FROM categories "
            "ORDER BY category_name"
        )
    ).mappings().all()

    # Load property condition records
    condition_records = PropertyCondition.query.filter_by(
        property_id=property_id
    ).order_by(
        PropertyCondition.id
    ).all()

    if request.method == "POST":

        property_code = request.form.get(
            "property_code", ""
        ).strip()

        property_name = request.form.get(
            "property_name", ""
        ).strip()

        category = request.form.get("category", "")

        location = request.form.get(
            "location", ""
        ).strip()

        date_acquired = request.form.get(
            "date_acquired", ""
        )

        # Validate required fields
        if not property_code or not property_name:

            flash(
                "Please complete all required fields.",
                "danger"
            )

            return redirect(
                url_for(
                    "property.edit_property",
                    property_id=property_id
                )
            )

        # Validate category and date
        try:

            category_id = int(category)

            valid_category_ids = {
                c["id"] for c in categories
            }

            if category_id not in valid_category_ids:
                raise ValueError

            acquired_date = (
                datetime.strptime(
                    date_acquired, "%Y-%m-%d"
                ).date()
                if date_acquired else None
            )

        except ValueError:

            flash("Invalid category or date.", "danger")

            return redirect(
                url_for(
                    "property.edit_property",
                    property_id=property_id
                )
            )

        # Check duplicate property code
        existing = Property.query.filter(
            Property.property_code == property_code,
            Property.id != property_id
        ).first()

        if existing:

            flash(
                "Property code already exists.",
                "danger"
            )

            return redirect(
                url_for(
                    "property.edit_property",
                    property_id=property_id
                )
            )

        # Update editable property information
        property.property_code = property_code
        property.property_name = property_name
        property.category_id = category_id
        property.location = location
        property.date_acquired = acquired_date

        # Save changes
        db.session.commit()

        flash(
            "Property updated successfully.",
            "success"
        )

        return redirect(
            url_for("property.list_properties")
        )

    return render_template(
        "edit_property.html",
        property=property,
        categories=categories,
        condition_records=condition_records
    )

# DELETE PROPERTY
@property_bp.route("/delete/<int:property_id>", methods=["POST"])
@login_required
def delete_property(property_id):

    # Find the selected property
    property = db.get_or_404(Property, property_id)

    # Prevent deletion of disposed properties
    if property.property_status == "Disposed":
        flash(
            "Disposed properties cannot be deleted.",
            "danger"
        )
        return redirect(
            url_for("property.list_properties")
        )

    # Check issuance history
    has_issuance = PropertyIssuance.query.filter_by(
        property_id=property_id
    ).first()

    # Check return history
    has_return = PropertyReturn.query.filter_by(
        property_id=property_id
    ).first()

    # Check transfer history
    has_transfer = db.session.execute(
        text(
            "SELECT id FROM property_transfers "
            "WHERE property_id = :pid LIMIT 1"
        ),
        {"pid": property_id}
    ).first()

    # Check disposal history
    has_disposal = db.session.execute(
        text(
            "SELECT id FROM property_disposals "
            "WHERE property_id = :pid LIMIT 1"
        ),
        {"pid": property_id}
    ).first()

    # Prevent deletion if transaction history exists
    if has_issuance or has_return or has_transfer or has_disposal:

        flash(
            "Cannot delete property with existing "
            "transaction history.",
            "danger"
        )

        return redirect(
            url_for("property.list_properties")
        )

    # Delete related condition records
    PropertyCondition.query.filter_by(
        property_id=property_id
    ).delete()

    # Delete the property
    db.session.delete(property)

    # Save changes
    db.session.commit()

    flash(
        "Property deleted successfully.",
        "success"
    )

    return redirect(
        url_for("property.list_properties")
    )

