============================================
Complete Authentication System For Flask App
============================================

Description
===========

The directory contains a user authentication system. It contains minimal Pyhon code (I believe :wink:)
and HTML code that we can add to our project with some minor changes.

The features:

- registration new users
- login with password and logout
- account confirmation system
- password resetting for unauthenticated users
- password changing for authenticated users
- updating account
- deleting account

To Do
=====

Few actions still need to be added:

- captcha



Usage
=====

Extend the code contained here. To do this, you need to add your own blueprints in the webapp package.

**Example**:

1. Create blue print package (in example package is titled as *timer*) and register it in *app.py* module:

    .. code::

        :
        ├─── webapp
        :    :
             |   app.py
             :
             ├───timer
             :   │   views.py
                 │   __init__.py
                 │
                 └───templates
                         time.html

    *views.py*:

    .. code:: python

        import datetime
        from flask import render_template
        from flask.views import View
        from flask_login import login_required

        from ..utils import Blueprint

        timer_blueprint = Blueprint('timer',  __name__, template_folder='templates')

        @service_blueprint.class_route('/time', 'time')
        class Time(View):
            init_every_request = False
            methods = ["GET"]
            template = 'time.html'
            decorators = [login_required]

            def dispatch_request(self):
                current_time = str(datetime.datetime.now())
                return render_template(self.template, current_time=current_time)

    *__init__.py*:

    .. code:: python

        from .views import time_blueprint

        __all__ = [
            'time_blueprint'
        ]

    *app.py*:

    .. code:: python

        # ...

        def register_blueprints(app: Flask) -> None:
            from .auth import auth_blueprint
            from .service import service_blueprint
            from .timer import timer_blueprint  # import it
            from .error import error_blueprint
            app.register_blueprint(auth_blueprint)
            app.register_blueprint(service_blueprint)
            app.register_blueprint(timer_blueprint)  # register it
            app.register_blueprint(error_blueprint)

        # ...

    *time.html*:

    .. code:: html

        <p>Current time: {{ current_time }}</p>

2. Test your changes in development mode:

    ``$ docker-compose -f docker/docker-compose.develop.yaml up``

    ``$ curl localhost:5000/time  # ofc, better is to do it in browser ;)``

3. Add tests of your blueprints:

    .. code::

        :
        ├─── tests
        :    :
             ├───timer
             :       test_views.py
                     __init__.py

    .. code:: python

        import pytest

        class TestTimeEndpoint:

        def test_getting_current_time(self, client):

            resp = client.get('/time')

            assert resp.status_code == 200

            html_page = resp.data.decode('utf-8')
            assert 'Current time' in html_page
