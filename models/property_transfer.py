
from extensions import db


class PropertyTransfer(db.Model):

    __tablename__ = "property_transfers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id"),
        nullable=False
    )

    from_location = db.Column(
        db.String(150),
        nullable=True
    )

    to_location = db.Column(
        db.String(150),
        nullable=True
    )

    transfer_date = db.Column(
        db.Date,
        nullable=False
    )

    transferred_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )
