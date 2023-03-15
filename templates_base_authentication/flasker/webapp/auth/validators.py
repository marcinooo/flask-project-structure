"""Contains validators of form fields."""

import re
from wtforms.validators import ValidationError
from wtforms import PasswordField, StringField
from flask_login import current_user

from .models import User


class PasswordType:  # pylint: disable=too-few-public-methods
    """
    Creates validator for password field. The validator checks if the password contains at least one letter,
    at least one number, and at least one capital letter.
    """

    def __init__(self, missing_number_message: str, missing_letter_message: str, missing_capital_letter_message: str):
        self.missing_number_message = missing_number_message
        self.missing_letter_message = missing_letter_message
        self.missing_capital_letter_message = missing_capital_letter_message

    def __call__(self, _, field: PasswordField) -> None:
        """Raises ValidationError if the required conditions are not met."""
        password = field.data
        if re.search('[0-9]', password) is None:
            raise ValidationError(self.missing_number_message)
        if re.search('[a-z]', password) is None:
            raise ValidationError(self.missing_letter_message)
        if re.search('[A-Z]', password) is None:
            raise ValidationError(self.missing_capital_letter_message)


class UniqueEmail:  # pylint: disable=too-few-public-methods
    """
    Class creates validator for email form field. Validator checks that the email is unique.
    """

    def __init__(self, message: str, skip_current_user: bool = False):
        self.message = message
        self.skip_current_user = skip_current_user

    def __call__(self, _, field: StringField) -> None:
        """Raises ValidationError if the required conditions are not met."""
        email = field.data
        user = User.find_by_email(email)
        if user:
            if not self.skip_current_user:
                raise ValidationError(self.message)
            if user.email != current_user.email:
                raise ValidationError(self.message)


class UniqueUsername:  # pylint: disable=too-few-public-methods
    """
    Class creates validator for username form field. Validator checks that the username is unique.
    """

    def __init__(self, message: str, skip_current_user: bool = False):
        self.message = message
        self.skip_current_user = skip_current_user

    def __call__(self, _, field: StringField) -> None:
        """Raises ValidationError if the required conditions are not met."""
        username = field.data
        user = User.find_by_username(username)
        if user:
            if not self.skip_current_user:
                raise ValidationError(self.message)
            if user.username != current_user.username:
                raise ValidationError(self.message)


class DeleteSlug:  # pylint: disable=too-few-public-methods
    """
    Creates validator for string field. The validator checks if the passed value equals to required constant value.
    """

    def __init__(self, message: str, required_slug: str):
        self.message = message
        self.required_slug = required_slug

    def __call__(self, _, field: StringField):
        """Raises ValidationError if the required conditions are not met."""
        slug = field.data
        if slug != self.required_slug:
            raise ValidationError(self.message)


class PasswordOfCurrentUser:  # pylint: disable=too-few-public-methods
    """
    Creates validator for password field. The validator checks if the password belongs to current logged user.
    """

    def __init__(self, message: str):
        self.message = message

    def __call__(self, _, field: PasswordField) -> None:
        """Raises ValidationError if the required conditions are not met."""
        password = field.data
        if not current_user.check_password(password):
            raise ValidationError(self.message)
