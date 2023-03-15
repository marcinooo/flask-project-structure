"""Contains auth blueprint utils."""

from functools import wraps
from typing import Callable
from flask_jwt_extended import get_jwt_identity

from ..utils import error_response
from ..models.users import User
from ..app import jwt, redis


def require_active_account(func: Callable):
    """
    Decorator to require active user account.

    :param func: endpoint to decorate
    :return: endpoint's response
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        if user and user.active:
            return func(*args, **kwargs)
        return error_response(message='Your account is inactive.', http_code=403, data={})
    return wrapper


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(_, jwt_payload: dict):
    """Checks if token was revoked."""
    jti = jwt_payload["jti"]
    token_in_redis = redis.get(jti)
    return token_in_redis is not None


@jwt.expired_token_loader
def expired_token_callback(_, __):
    """Custom error callback."""
    return error_response(message='Token has expired.', http_code=401, data={})


@jwt.revoked_token_loader
def revoked_token_callback(_, __):
    """Custom error callback."""
    return error_response(message='Token has been revoked.', http_code=401, data={})


@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Custom error callback."""
    return error_response(message=f'{error}.', http_code=422, data={})
