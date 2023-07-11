"""DB schema."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Float,
    String,
    UniqueConstraint,
    sql,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
db = SQLAlchemy(app)


class DriverTable(db.Model):
    """Stores the information about a driver."""

    __tablename__ = "driver"

    messenger_id = Column(BigInteger, primary_key=True)
    phone = Column(String, nullable=False)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    route = Column(String, nullable=False)
    last_update = Column(
        DateTime(),
        nullable=False,
        server_default=sql.func.now(),
        onupdate=sql.func.now(),
    )
    state = Column(Enum("connected", "disabled", name="state"), nullable=False)

    def __repr__(self):
        """Representation."""
        return (
            f"<Driver(messenger_id={self.messenger_id!r}, phone={self.phone!r}, name={self.name!r}"
            f"latitude={self.latitude!r}, last_name={self.longitude!r}, "
            f"last_update={self.last_update!r}, state={self.state!r}, route={self.route!r}>"
        )

    __table_args__ = (
        UniqueConstraint("phone"),
        CheckConstraint("-90 < latitude AND latitude < 90"),
        CheckConstraint("-180 < longitude AND longitude < 180"),
    )
