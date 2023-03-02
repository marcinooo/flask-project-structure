"""Contains auth utils."""

from typing import Callable
from functools import wraps
from flask import redirect, url_for, abort
from flask_login import current_user

from ..app import login_manager
from .models import User, Permission


@login_manager.user_loader
def load_user(user_id: int) -> User:
    """
    Assigns a user object to the global current_user variable.

    :param user_id: id of user to assigne
    :return: User instance
    """
    return User.find_by_id(user_id)


def redirect_authenticated_users(func: Callable) -> Callable:
    """
    The decorator redirects authenticated users to note view.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('service.home'))
        return func(*args, **kwargs)
    return wrapper


def permission_required(permission):
    """
    The decorator checks if user has given permission to access view.
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(func):
    """
    The decorator checks if user is superuser.
    """
    return permission_required(Permission.ADMINISTER)(func)
