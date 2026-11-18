
from extensions import db


class PropertyIssuance(db.Model):

    __tablename__ = "property_issuances"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id"),
        nullable=False
    )

    issued_to = db.Column(
        db.String(100),
        nullable=False
    )

    position = db.Column(
        db.String(100)
    )

    office_room = db.Column(
        db.String(100)
    )

    date_issued = db.Column(
        db.Date,
        nullable=False
    )

    condition_status = db.Column(
        db.String(50)
    )

    remarks = db.Column(
        db.Text
    )

    issued_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )
