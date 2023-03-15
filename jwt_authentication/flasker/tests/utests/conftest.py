import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch
from flask_jwt_extended import create_access_token, create_refresh_token

from .utils import Redis

project_root_dir_path = Path(__file__).parents[2]
sys.path.append(str(project_root_dir_path))

os.environ["FLASK_ENV"] = 'testing'

from webapp import create_app, db, users_models


@pytest.fixture
def app():
    with patch('webapp.redis_manager.Redis', Redis):
        yield create_app()


@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def access_token(user, app):
    yield create_access_token(identity=user.id, expires_delta=app.config['ACCESS_EXPIRES'], fresh=True)


@pytest.fixture
def refresh_token(user, app):
    yield create_refresh_token(identity=user.id, expires_delta=app.config['REFRESH_EXPIRES'])


@pytest.fixture
def user():
    password_hash = users_models.User.generate_password_hash('Jofken35')
    new_user = users_models.User(username='John', email='john.kennedy@gmail.com', password=password_hash)
    user.active = True
    new_user.save_to_db()
    yield new_user
    new_user.delete_from_db()


@pytest.fixture
def inactive_user():
    password_hash = users_models.User.generate_password_hash('Jofken35')
    new_user = users_models.User(username='John', email='john.kennedy@gmail.com', password=password_hash)
    new_user.save_to_db()
    yield new_user
    new_user.delete_from_db()
