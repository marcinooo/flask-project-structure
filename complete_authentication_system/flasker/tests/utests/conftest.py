import os
import sys
import pytest
from pathlib import Path

project_root_dir_path = Path(__file__).parents[2]
sys.path.append(str(project_root_dir_path))

os.environ["FLASK_ENV"] = 'testing'

from webapp import create_app, db, auth_models


def request_loader(client, user):
    """
    The function load user. It allows make authenticated client in tests.
    :param client: test client
    :param user: User to load
    :return: None
    """
    @client.application.login_manager.request_loader
    def load_user_from_request(_):
        return user


@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def auth_client(client, user):
    user.active = True
    user.save_to_db()

    request_loader(client, user)
    yield client
    request_loader(client, None)


@pytest.fixture
def user():
    password_hash = auth_models.User.generate_password_hash('Jofken35')
    new_user = auth_models.User(username='John',
                                email='john.kennedy@gmail.com',
                                password=password_hash)
    new_user.save_to_db()
    yield new_user
    new_user.delete_from_db()
