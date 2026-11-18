
from extensions import db


class PropertyDisposal(db.Model):
    __tablename__ = "property_disposals"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id"),
        nullable=False
    )

    disposal_date = db.Column(
        db.Date,
        nullable=False
    )

    reason = db.Column(
        db.String(255),
        nullable=False
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    disposed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )
