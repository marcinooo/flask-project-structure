import pytest

from webapp import auth_models
from webapp.auth import tasks


class MockDelay:
    @staticmethod
    def delay():
        pass


class TestRegisterEndpoint:
    """The class tests '/register' endpoint."""

    def test_registration(self, client, monkeypatch):

        def mock_delay(*args, **kwargs):
            return MockDelay()

        monkeypatch.setattr(tasks.send_account_activation_email, "delay", mock_delay)

        data = {
            'username': 'Abraham',
            'email': 'abraham.lincoln@gmail.com',
            'password': 'Abrlin16',
            'confirm_password': 'Abrlin16'
        }
        resp = client.post('/register', data=data, follow_redirects=True)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert '[success]' in html_page
        new_user = auth_models.User.find_by_username('Abraham')
        assert new_user and not new_user.active

    def test_registration_with_existing_username_in_db(self, client, user):
        data = {
            'username': 'John',
            'email': 'abraham.lincoln@gmail.com',
            'password': 'Abrlin16',
            'confirm_password': 'Abrlin16'
        }
        resp = client.post('/register', data=data)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert 'This username is already taken.' in html_page

    def test_registration_with_existing_email_in_db(self, client, user):
        data = {
            'username': 'Abraham',
            'email': 'john.kennedy@gmail.com',
            'password': 'Abrlin16',
            'confirm_password': 'Abrlin16'
        }
        resp = client.post('/register', data=data)

        html_page = resp.data.decode('utf-8')
        assert 'This email is already taken, please select another one.' in html_page

    def test_registration_with_invalid_form_fields(self, client):
        data = {
            'username': 'A',
            'email': 'Invalid mail',
            'password': 'bad',
            'confirm_password': 'bad :(',
        }
        resp = client.post('/register', data=data)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        returned_messages = [
            'Invalid email address.',
            'Field must be between 3 and 50 characters long.',
            'Make sure your password has a number in it.',
            'Field must be equal to password.',
        ]
        assert all([msg in html_page for msg in returned_messages])


class TestLoginEndpoint:
    """The class tests '/login' endpoint."""

    @pytest.mark.parametrize('email,password,message', [
        ('john.kennedy@gmail.com', 'Ohh', 'Invalid email or password!'),
        ('fake@mail.com', 'Jofken35', 'Invalid email or password!')
    ])
    def test_login_with_invalid_credentials(self, client, user, email, password, message):
        data = {
            'email': email,
            'password': password
        }
        resp = client.post('/login', data=data, follow_redirects=True)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert message in html_page

    def test_login_with_valid_credentials_and_inactive_account(self, client, user):
        data = {
            'email': 'john.kennedy@gmail.com',
            'password': 'Jofken35'
        }
        resp = client.post('/login', data=data)

        assert resp.status_code == 302
        html_page = resp.data.decode('utf-8')
        assert 'Redirecting...' in html_page
        assert not user.active

    def test_login_with_valid_credentials_and_active_account(self, client, user):
        # Prepare user
        user.active = True
        user.save_to_db()
        # Test endpoint

        data = {
            'email': 'john.kennedy@gmail.com',
            'password': 'Jofken35'
        }
        resp = client.post('/login', data=data, follow_redirects=True)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert 'Main app content' in html_page


class TestActivateAccountEndpoint:
    """The class tests '/confirm/<token>' endpoint."""

    def test_activate_account_with_valid_token_request(self, auth_client, user):
        expire_time = 15  # in seconds
        token = user.generate_jwt_token(expire_time=expire_time)
        resp = auth_client.get(f'/confirm/{token}', follow_redirects=True)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert 'You have confirmed your account.' in html_page

    def test_activate_account_with_invalid_token_request(self, auth_client, user):
        token = 'yJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2NTQxNzEyOTEuNjY1MjgyNX0.' \
                'gImT1StADPQ-fd0jc0PkYHiQjYbudiK3ODXBFxIzMf4'
        resp = auth_client.get(f'/confirm/{token}', follow_redirects=True)

        assert resp.status_code == 404


class TestResetPasswordEndpoint:
    """The class tests '/reset-password/<token>' endpoint."""

    def test_reset_password_with_valid_token_request(self, client, user):
        expire_time = 15  # in seconds
        token = user.generate_jwt_token(expire_time=expire_time)
        data = {
            'password': 'Jofken99',
            'confirm_password': 'Jofken99'
        }
        resp = client.post(f'/reset-password/{token}', data=data, follow_redirects=True)

        html_page = resp.data.decode('utf-8')
        assert resp.status_code == 200 and 'Your password has been reset.' in html_page


class TestAccountEndpoint:
    """The class tests '/account' endpoint."""

    def test_account(self, auth_client, user):
        resp = auth_client.get('/account')

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert user.username in html_page
        assert user.email in html_page


class TestAccountUpdateEndpoint:
    """The class tests '/account/update' endpoint."""

    def test_account_update_with_valid_data(self, auth_client):
        data = {
            'username': 'Abraham',
            'email': 'abraham.lincoln@gmail.com',
        }
        resp = auth_client.post('/account/update', data=data, follow_redirects=True)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert 'Abraham' in html_page
        assert 'abraham.lincoln@gmail.com' in html_page

    def test_account_update_with_invalid_data(self, auth_client):
        data = {
            'username': 'Valid',
            'email': 'Invalid',
        }
        resp = auth_client.post('/account/update', data=data, follow_redirects=True)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        print(html_page)


class TestAccountDeleteEndpoint:

    def test_account_successfully_delete(self, auth_client):
        data = {'slug': 'delete'}
        resp = auth_client.post('/account/delete', data=data, follow_redirects=True)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert 'Your account has been deleted successfully.' in html_page

    def test_account_delete_with_invalid_slug(self, auth_client):
        data = {'slug': 'fake'}
        resp = auth_client.post('/account/delete', data=data, follow_redirects=True)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert 'Invalid slug.' in html_page


class TestChangePasswordEndpoint:

    def test_change_password(self, auth_client, user):
        data = {
            'old_password': 'Jofken35',
            'new_password': 'Jofken34',
            'confirm_new_password': 'Jofken34'
        }
        resp = auth_client.post('/account/change-password', data=data, follow_redirects=True)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert 'Your password has been changed successfully.' in html_page

    def test_change_password_with_invalid_form_fields(self, auth_client, user):
        data = {
            'old_password': 'Jofken35',
            'new_password': 'aaa',
            'confirm_new_password': 'b'
        }
        resp = auth_client.post('/account/change-password', data=data, follow_redirects=True)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        returned_messages = [
            'Field must be between 6 and 100 characters long.',
            'Make sure your password has a number in it.',
            'Field must be equal to new_password.',
        ]
        assert all([msg in html_page for msg in returned_messages])

    def test_change_password_with_invalid_old_password(self, auth_client, user):
        data = {
            'old_password': ':)',
            'new_password': 'Jofken34',
            'confirm_new_password': 'Jofken34'
        }
        resp = auth_client.post('/account/change-password', data=data, follow_redirects=True)

        assert resp.status_code == 200
        html_page = resp.data.decode('utf-8')
        assert 'Invalid current password.' in html_page


