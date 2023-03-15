"""Contains base class for all models."""
from sqlalchemy.ext.declarative import declared_attr

from ..app import db


class BaseMixin:
    """Base class which is common for other models."""

    @declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        return cls.__name__.lower()

    id = db.Column(db.Integer, primary_key=True)

    def save_to_db(self) -> None:
        """Saves model to database."""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        """Deletes model from database."""
        db.session.delete(self)
        db.session.commit()
