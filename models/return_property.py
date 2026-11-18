
from extensions import db


class PropertyReturn(db.Model):

    __tablename__ = "property_returns"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id"),
        nullable=False
    )

    returned_by = db.Column(
        db.String(100),
        nullable=False
    )

    date_returned = db.Column(
        db.Date,
        nullable=False
    )

    condition_status = db.Column(
        db.String(50)
    )

    remarks = db.Column(
        db.Text
    )

    received_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )
