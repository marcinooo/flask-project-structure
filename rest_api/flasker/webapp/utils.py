"""Contains common utils for flasker app."""

from typing import Callable
from functools import wraps
from flask import request
from pydantic import ValidationError


class MissingBodyArgument(Exception):
    """Throws when decorated function doesn't contain 'body' argument."""


def error_response(message, http_code, data=None) -> tuple[dict, int]:
    """
    Creates error dictionary structure and attach http code to it.
    :param message: message to return in body
    :param http_code: http response code
    :param data: data to return in body
    :return:
    """
    response = {
        'message': message,
        'category': 'error',
        'data': data
    }
    return response, http_code


def success_response(message, http_code, data=None):
    """
    Creates success dictionary structure and attach http code to it.
    :param message: message to return in body
    :param http_code: http response code
    :param data: data to return in body
    :return:
    """
    response = {
        'message': message,
        'category': 'success',
        'data': data
    }
    return response, http_code


def use_schema(func: Callable) -> Callable:
    """
    Decorator to parse request body with Pydantic features.
    :param func: endpoint to decorate
    :return: endpoint's response
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        body_schema = func.__annotations__.get("body")
        if body_schema is None:
            raise MissingBodyArgument("`use_schema` decorator requires 'body' argument in decorated function.")
        if not request.is_json:
            msg = 'Did not attempt to load JSON data because the request Content-Type was not \'application/json\'.'
            return error_response(message=msg, http_code=400)
        body_params = request.get_json()
        try:
            dumped_schema = body_schema(**body_params)
            kwargs['body'] = dumped_schema
        except ValidationError as err:
            return error_response(message='Validation error.', http_code=400, data={'validation_errors': err.errors()})
        return func(*args, **kwargs)
    return wrapper
