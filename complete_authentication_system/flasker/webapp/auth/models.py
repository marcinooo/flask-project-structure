"""Contains database models for auth blueprint."""

import time
import datetime
from typing import ClassVar
from dataclasses import dataclass
from jwt import encode as encode_jwt_token, decode as decode_jwt_token
from flask import current_app
from sqlalchemy.ext.declarative import declared_attr
from flask_login import UserMixin

from ..app import db, bcrypt


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


class User(UserMixin, BaseMixin, db.Model):
    """ Creates object which is representation of app user."""

    __tablename__ = 'users'

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    active = db.Column(db.Boolean(), default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # pylint: disable=access-member-before-definition
        if self.role is None:
            if self.email in current_app.config['ADMINISTRATOR_MAILS']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        # pylint: enable=access-member-before-definition

    def check_password(self, password: str) -> bool:
        """
        Checks if the passed password matches the user's password.

        :param password: password to check
        :return: True if passwords match, otherwise False
        """
        return bcrypt.check_password_hash(self.password, password)

    def generate_jwt_token(self, expire_time: int = 600) -> str:
        """
        Creates jwt token which is valid in given time.

        :param expire_time: time to expire token
        :return: jwt token
        """
        return encode_jwt_token(
            {'user_id': self.id, 'exp': time.time() + expire_time},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        )

    def can(self, permissions: int):
        """
        Checks if user's role has given permission.

        :param permissions:
        :return: True if role is appropriate, otherwise False
        """
        return self.role is not None and (self.role.permissions & permissions) == permissions

    @classmethod
    def find_by_id(cls, _id: int) -> 'User':
        """
        Returns user based on the given user id.

        :param _id: user id
        :return: user with the given id or None
        """
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_username(cls, username: str) -> 'User':
        """
        Returns user based on the given user username.

        :param username: username
        :return: user with the given username or None
        """
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> 'User':
        """
        Returns user based on the given user email.

        :param email: user's email
        :return: user with the given email or None
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def generate_password_hash(cls, password: str) -> str:
        """
        Generates hash for given password.

        :param password: password
        :return: password's hash
        """
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @classmethod
    def verify_jwt_token(cls, token: str) -> 'User':
        """
        Validates jwt token.

        :param token: token
        :return: founded user, otherwise None
        """
        try:
            user_id = decode_jwt_token(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['user_id']
            user = User.query.get(user_id)
        except Exception:  # pylint: disable=broad-except
            user = None
        return user

    def __repr__(self) -> str:
        """
        Returns user representation.

        :return: user string representation
        """
        return f"User('{self.email}')"


@dataclass
class Permission:
    """Users permissions."""
    CLIENT: ClassVar[int] = 0x01
    ADMINISTER: ClassVar[int] = 0x80


class Role(db.Model, BaseMixin):
    """User's role."""

    __tablename__ = 'roles'

    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def save_all_to_db():
        """
        Inserts new roles in database.
        :return: None
        """
        raw_roles = {
            'User': (Permission.CLIENT, True),
            'Administrator': (0xff, False)
        }
        for name, artifacts in raw_roles.items():
            role = Role.query.filter_by(name=name).first()
            if role is None:
                role = Role(name=name)
            role.permissions = artifacts[0]
            role.default = artifacts[1]
            db.session.add(role)
            db.session.commit()
