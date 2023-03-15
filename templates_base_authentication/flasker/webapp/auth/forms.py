"""Contains forms for auth blueprint."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from .validators import PasswordType, UniqueEmail, UniqueUsername, DeleteSlug, PasswordOfCurrentUser


class RegistrationForm(FlaskForm):
    """Gets user data during registration."""

    username = StringField(
        'Username',
        validators=[
            DataRequired('This field is required.'),
            Length(min=3, max=50),
            UniqueUsername('This username is already taken.'),
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired('This field is required.'),
            Length(min=5, max=100),
            Email(),
            UniqueEmail('This email is already taken, please select another one.'),
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired('This field is required.'),
            Length(min=6, max=100),
            PasswordType(
                'Make sure your password has a number in it.',
                'Make sure your password has a letter in it.',
                'Make sure your password has a capital letter in it.'
            ),
        ]
    )

    confirm_password = PasswordField(
        'Password confirmation',
        validators=[
            DataRequired('This field is required.'),
            EqualTo('password'),
        ]
    )

    submit = SubmitField(
        'Register'
    )


class LoginForm(FlaskForm):
    """Gets user credentials during authentication."""

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
        ]
    )

    remember = BooleanField(
        'Remember me'
    )

    submit = SubmitField(
        'Log in'
    )


class ResetPasswordEmailForm(FlaskForm):
    """Gets email to send reset password mali."""

    email = StringField(
        'Email',
        validators=[
            DataRequired('This field is required.'),
            Email(),
        ]
    )

    submit = SubmitField(
        'Send'
    )


class ResetPasswordCredentialsForm(FlaskForm):
    """Gets new user password to reset old password."""

    password = PasswordField(
        'Password',
        validators=[
            DataRequired('This field is required.'),
            Length(min=6, max=100),
            PasswordType(
                'Make sure your password has a number in it.',
                'Make sure your password has a letter in it.',
                'Make sure your password has a capital letter in it.'
            ),
        ]
    )

    confirm_password = PasswordField(
        'Password confirmation',
        validators=[
            DataRequired('This field is required.'),
            EqualTo('password'),
        ]
    )

    submit = SubmitField(
        'Set'
    )


class AccountUpdateForm(FlaskForm):
    """Gets user data to update information about him."""

    username = StringField(
        'Username',
        validators=[
            Length(min=3, max=50),
            UniqueUsername('This username is already taken.', skip_current_user=True),
        ]
    )

    email = StringField(
        'Email',
        validators=[
            Length(min=5, max=100),
            Email(),
            UniqueEmail('This email is already taken, please select another one.', skip_current_user=True),
        ]
    )

    submit = SubmitField(
        'Update'
    )


class DeleteAccountForm(FlaskForm):
    """Gets confirmation slug during deletions account."""

    REQUIRED_SLUG = 'delete'

    slug = StringField(
        'Confirm deletion',
        validators=[
            DeleteSlug(f'Invalid slug. Please type "{REQUIRED_SLUG}" to delete your account.', REQUIRED_SLUG),
        ]
    )

    submit = SubmitField(
        'Delete'
    )


class ChangePasswordForm(FlaskForm):
    """Get new user password to change."""

    old_password = PasswordField(
        'Current password',
        validators=[
            DataRequired('This field is required.'),
            PasswordOfCurrentUser('Invalid current password.'),
        ]
    )

    new_password = PasswordField(
        'New password',
        validators=[
            DataRequired('This field is required.'),
            Length(min=6, max=100),
            PasswordType(
                'Make sure your password has a number in it.',
                'Make sure your password has a letter in it.',
                'Make sure your password has a capital letter in it.'
            ),
        ]
    )

    confirm_new_password = PasswordField(
        'New password confirmation',
        validators=[
            DataRequired('This field is required.'),
            EqualTo('new_password'),
        ]
    )

    submit = SubmitField(
        'Change'
    )
