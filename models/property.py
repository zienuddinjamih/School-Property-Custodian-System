from extensions import db


class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True)

    property_code = db.Column(
        db.String(50), unique=True, nullable=False
    )

    property_name = db.Column(
        db.String(100), nullable=False
    )

    category_id = db.Column(db.Integer, nullable=True)

    description = db.Column(db.Text, nullable=True)

    serial_number = db.Column(db.String(100), nullable=True)

    quantity = db.Column(db.Integer, nullable=False, default=1)

    unit_cost = db.Column(db.Numeric(10, 2), nullable=True)

    date_acquired = db.Column(db.Date, nullable=True)

    condition_status = db.Column(
        db.String(50), default="Good"
    )

    property_status = db.Column(
        db.String(50), default="Available"
    )

    location = db.Column(db.String(150), nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    def __repr__(self):
        return f"<Property {self.property_name}>"