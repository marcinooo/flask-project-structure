"""Contains functions to build main instance of flasker app."""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
session = Session()


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


def register_blueprints(app: Flask) -> None:
    """
    Registers given blueprints in Flask app instance.

    :param app: instance of Flask app
    :return: None
    """
    # pylint: disable=import-outside-toplevel
    from .auth import auth_blueprint
    from .service import service_blueprint
    from .error import error_blueprint
    # pylint: enable=import-outside-toplevel
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(service_blueprint)
    app.register_blueprint(error_blueprint)


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
    static_folder_path = project_root_dir_path / 'webapp' / 'static'

    load_configuration(project_root_dir_path)
    app = Flask(__name__, static_folder=str(static_folder_path), template_folder=str(templates_folder_path),
                instance_relative_config=True)
    app.config.from_pyfile(str(settings_path))

    register_logger(app, project_root_dir_path)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    session.init_app(app)

    register_blueprints(app)

    return app


# pylint: disable=wrong-import-position,unused-import
from .auth import models as auth_models
