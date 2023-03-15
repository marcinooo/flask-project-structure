"""Contains auth schemas."""

from pydantic import BaseModel, validator

from .field_validators import (email_required, email_is_unique, username_is_alfa_numeric, username_is_unique,
                               password_required, value_equals_to)


class UserLoginSchema(BaseModel):
    """Handles login data."""
    email: str
    password: str

    @validator('email')
    def email_validator(cls, value):  # pylint: disable=no-self-argument
        """Validates user email."""
        email_required(value)
        return value


class UserRegisterSchema(BaseModel):
    """Handles registration data."""
    username: str
    email: str
    password: str
    password_confirm: str

    @validator('username')
    def username_validator(cls, value):  # pylint: disable=no-self-argument
        """Validates user username."""
        username_is_alfa_numeric(value)
        username_is_unique(value)
        return value

    @validator('email')
    def email_validator(cls, value):  # pylint: disable=no-self-argument
        """Validates user email."""
        email_required(value)
        email_is_unique(value)
        return value

    @validator('password')
    def password_validator(cls, value):  # pylint: disable=no-self-argument
        """Validates user password."""
        password_required(value)
        return value

    @validator('password_confirm')
    def password_confirm_validator(cls, value, values, **kwargs):  # pylint: disable=unused-argument,no-self-argument
        """Validates user password confirmation."""
        value_equals_to(value=value, equals_to='password', all_values=values, message='Passwords do not match.')
        return value


class ConfirmTokenSchema(BaseModel):
    """Handles token to confirm account."""
    token: str


class PasswordResetEmailSchema(BaseModel):
    """Handles email to send reset link."""
    email: str

    @validator('email')
    def email_validator(cls, value):  # pylint: disable=no-self-argument
        """Validates user email."""
        email_required(value)
        return value


class PasswordResetSchema(BaseModel):
    """Handles new user password."""
    token: str
    password: str
    password_confirm: str

    @validator('password')
    def password_validator(cls, value):  # pylint: disable=no-self-argument
        """Validates user password."""
        password_required(value)
        return value

    @validator('password_confirm')
    def password_confirm_validator(cls, value, values, **kwargs):  # pylint: disable=unused-argument,no-self-argument
        """Validates user password confirmation."""
        value_equals_to(value=value, equals_to='password', all_values=values, message='Passwords do not match.')
        return value


class PasswordChangeSchema(BaseModel):
    """Handles new user password."""
    old_password: str
    password: str
    password_confirm: str

    @validator('password')
    def password_validator(cls, value):  # pylint: disable=no-self-argument
        """Validates user password."""
        password_required(value)
        return value

    @validator('password_confirm')
    def password_confirm_validator(cls, value, values, **kwargs):  # pylint: disable=unused-argument,no-self-argument
        """Validates user password confirmation."""
        value_equals_to(value=value, equals_to='password', all_values=values, message='Passwords do not match.')
        return value
