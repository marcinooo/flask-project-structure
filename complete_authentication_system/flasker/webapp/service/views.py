"""Contains views for service blueprint."""

from flask import render_template
from flask.views import View
from flask_login import login_required

from ..utils import Blueprint
from ..auth.utils import admin_required


service_blueprint = Blueprint('service',  __name__, template_folder='templates')


@service_blueprint.class_route('/', 'home')
class Home(View):
    """Example of service home page."""
    init_every_request = False
    methods = ["GET"]
    template = 'home.html'
    decorators = [login_required]

    def dispatch_request(self):
        return render_template(self.template)


@service_blueprint.class_route('/admin', 'admin')
class Admin(View):
    """Example of admin page."""
    init_every_request = False
    methods = ["GET"]
    template = 'admin.html'
    decorators = [login_required, admin_required]

    def dispatch_request(self):
        return render_template(self.template)
