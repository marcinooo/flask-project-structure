"""Contains functions to build main instance of flasker app."""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from .redis_manager import RedisManager


db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
redis = RedisManager()


def load_configuration(project_root_dir: Path) -> None:
    """
    Loads configuration based on FLASK_ENV variable.

    :raises NotImplementedError: if FLASK_ENV variable is not set
    :param project_root_dir: path to project root directory
    :return: None
    """
    environment = os.environ.get('FLASK_ENV')
    if environment == 'development':
        load_dotenv(str(project_root_dir / 'environment' / '.env.development'))
    elif environment == 'production':
        load_dotenv(str(project_root_dir / 'environment' / '.env.production'))
    elif environment == 'testing':
        load_dotenv(str(project_root_dir / 'environment' / '.env.testing'))
    else:
        raise NotImplementedError(f'Please set "FLASK_ENV" variable to "development" or "production", or "testing". '
                                  f'Current value: {environment}')


def add_resources(api: Api):
    """
    Adds authentication endpoints.

    :param api: instance of Flask Api extension
    :return: None
    """
    # pylint: disable=import-outside-toplevel
    from .resources.users import UserResource
    # pylint: enable=import-outside-toplevel
    api.add_resource(UserResource, '/user/<int:user_id>')


def add_auth(app: Flask):
    """
    Adds authentication endpoints.

    :param app: instance of Flask app
    :return: None
    """
    # pylint: disable=import-outside-toplevel
    from .auth import auth_blueprint
    # pylint: enable=import-outside-toplevel
    app.register_blueprint(auth_blueprint)


def register_logger(app, project_root_dir) -> None:
    """
    Setup main app logger.

    :param app: instance of Flask app
    :param project_root_dir: path to project root directory
    :return: None
    """
    log_dir = project_root_dir / 'logs'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    file_handler = RotatingFileHandler(log_dir / 'main.log', maxBytes=10_000_000,  backupCount=30)
    file_handler.setFormatter(
        logging.Formatter('[%(asctime)s] [%(levelname)8s] %(message)s (in %(pathname)s:%(lineno)d)')
    )
    file_handler.setLevel(logging.INFO)
    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.info('Flasker started')


def create_app() -> Flask:
    """
    Creates flasker app.

    :return: flasker app instance
    """
    project_root_dir_path = Path(__file__).parents[1]
    settings_path = project_root_dir_path / 'settings.py'
    templates_folder_path = project_root_dir_path / 'webapp' / 'templates'

    load_configuration(project_root_dir_path)
    app = Flask(__name__, template_folder=str(templates_folder_path))
    app.config.from_pyfile(str(settings_path))

    register_logger(app, project_root_dir_path)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    redis.init_app(app)

    add_auth(app)

    with app.app_context():
        api = Api(app)
        add_resources(api)

    return app


# pylint: disable=wrong-import-position,unused-import
from .models import users as users_models
