"""Contains schema filed validators."""

import re

from ..models.users import User


def email_required(value, message='Email address is invalid.'):
    """
    Checks if value has email format.

    :param value: value to validate
    :param message: message of error
    :return: passed value
    """
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not re.fullmatch(regex, value):
        raise ValueError(message)
    return value


def email_is_unique(value, message='This email is already taken.'):
    """
    Checks if email is not used by other users.

    :param value: value to validate
    :param message: message of error
    :return: passed value
    """
    user = User.find_by_email(value)
    if user is not None:
        raise ValueError(message)
    return value


def username_is_alfa_numeric(value, message='Username must be alphanumeric.'):
    """
    Checks if value is alfa numeric.

    :param value: value to validate
    :param message: message of error
    :return: passed value
    """
    if not value.isalnum():
        raise ValueError(message)
    return value


def username_is_unique(value, message='This username is already taken.'):
    """
    Checks if username is not used by other users.

    :param value: value to validate
    :param message: message of error
    :return: passed value
    """
    user = User.find_by_username(value)
    if user is not None:
        raise ValueError(message)
    return value


def password_required(value,
                      missing_number_message='Make sure your password has a number in it.',
                      missing_letter_message='Make sure your password has a letter in it.',
                      missing_capital_letter_message='Make sure your password has a capital letter in it.'):
    """
    Checks if value match to password pattern.

    :param value: value to check
    :param missing_number_message: message of error if value does not contain digit
    :param missing_letter_message: message of error if value does not contain letter
    :param missing_capital_letter_message: message of error if value does not contain capital letter
    :return: passed value
    """
    if re.search('[0-9]', value) is None:
        raise ValueError(missing_number_message)
    if re.search('[a-z]', value) is None:
        raise ValueError(missing_letter_message)
    if re.search('[A-Z]', value) is None:
        raise ValueError(missing_capital_letter_message)
    return value


def value_equals_to(value, equals_to, all_values, message='Field value and "{}" do not match.'):
    """
    Checks if filed value matches to other schema filed.
    :param value: value of filed which is validated
    :param equals_to: filed name which is required to be the same as current
    :param all_values: all filed values
    :param message: message of error
    :return: passed value
    """
    if equals_to in all_values and value != all_values[equals_to]:
        raise ValueError(message.format(equals_to))
    return value
