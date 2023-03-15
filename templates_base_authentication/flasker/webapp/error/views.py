"""Contains views for error blueprint."""

from flask import render_template

from ..utils import Blueprint


error_blueprint = Blueprint('error',  __name__, template_folder='templates')


@error_blueprint.app_errorhandler(404)
def page_not_found(_):
    """Renders 404 error page."""
    return render_template('404.html'), 404


@error_blueprint.app_errorhandler(403)
def page_forbidden(_):
    """Renders 403 error page."""
    return render_template('403.html'), 403


@error_blueprint.app_errorhandler(500)
def page_internal_server_error(_):
    """Renders 500 error page."""
    return render_template('500.html'), 500
