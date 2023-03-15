"""Contains database models for auth blueprint."""

import time
import datetime
from jwt import encode as encode_jwt_token, decode as decode_jwt_token
from flask import current_app

from ..app import db, bcrypt
from .base import BaseMixin


class User(BaseMixin, db.Model):
    """Creates object which is representation of app user."""

    __tablename__ = 'users'

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    active = db.Column(db.Boolean(), default=False)

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
