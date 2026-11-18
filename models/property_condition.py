
from extensions import db


class PropertyCondition(db.Model):
    __tablename__ = "property_conditions"

    id = db.Column(db.Integer, primary_key=True)

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id"),
        nullable=False
    )

    condition_status = db.Column(
        db.String(50),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    __table_args__ = (
        db.UniqueConstraint(
            "property_id",
            "condition_status",
            name="uq_property_condition"
        ),
    )

    def __repr__(self):
        return (
            f"<PropertyCondition "
            f"{self.condition_status}: {self.quantity}>"
        )
