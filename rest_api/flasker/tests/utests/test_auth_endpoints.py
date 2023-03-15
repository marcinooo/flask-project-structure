import json
import pytest
from unittest.mock import patch, Mock

from webapp import users_models


class TestAuthEndpoints:
    """The class tests '/auth/register' endpoints."""

    @patch('webapp.tasks.email.send_account_activation_email', Mock())
    def test_register(self, client):

        resp = client.post('/auth/register', json={
            'username': 'Abraham',
            'email': 'abraham.lincoln@gmail.com',
            'password': 'Abrlin16',
            'password_confirm': 'Abrlin16'
        })

        assert resp.status_code == 201

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('category') == 'success'
        assert 'was created successfully' in resp_data.get('message')

        new_user = users_models.User.find_by_username('Abraham')
        assert new_user and not new_user.active

    @pytest.mark.parametrize('email,password,response_code,response_data', [
        ('john.kennedy@gmail.com', 'Ohh', 401, {'message': 'Invalid credentials.', 'data': {}, 'category': 'error'}),
        ('fake@mail.com', 'Jofken35', 401, {'message': 'Invalid credentials.', 'data': {}, 'category': 'error'}),
        ('john.kennedy@gmail.com', 'Jofken35', 200, {'message': 'Login successful.', 'data': {'': ''}, 'category': 'success'}),
    ])
    def test_login(self, client, user, email, password, response_code, response_data):
        resp = client.post('/auth/login', json={
            'email': email,
            'password': password
        })
        assert resp.status_code == response_code

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('message') == response_data.get('message')
        assert resp_data.get('category') == response_data.get('category')
        if response_data.get('data'):
            assert 'access_token' in resp_data.get('data') and 'refresh_token' in resp_data.get('data')

    def test_revoke_access_token(self, client, access_token, user):
        resp = client.get(f'/user/{user.id}', headers={'Authorization': f'Bearer {access_token}'})
        assert resp.status_code == 200

        resp = client.delete('/auth/revoke-access-token', headers={'Authorization': f'Bearer {access_token}'})
        assert resp.status_code == 200

        resp = client.get(f'/user/{user.id}', headers={'Authorization': f'Bearer {access_token}'})
        assert resp.status_code == 401
        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('category') == 'error'
        assert resp_data.get('message') == 'Token has been revoked.'

    def test_revoke_refresh_token(self, client, refresh_token):
        resp = client.delete('/auth/revoke-refresh-token', headers={'Authorization': f'Bearer {refresh_token}'})
        assert resp.status_code == 200

        resp = client.post('/auth/refresh', headers={'Authorization': f'Bearer {refresh_token}'})
        assert resp.status_code == 401
        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('category') == 'error'
        assert resp_data.get('message') == 'Token has been revoked.'

    def test_refresh_token(self, client, access_token, refresh_token):
        resp = client.post('/auth/refresh', headers={'Authorization': f'Bearer {refresh_token}'})
        assert resp.status_code == 200

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('message') == 'Refresh successful.'
        assert resp_data.get('category') == 'success'
        assert 'access_token' in resp_data.get('data') and 'refresh_token' in resp_data.get('data')

        resp = client.post('/auth/refresh', headers={'Authorization': f'Bearer {access_token}'})
        assert resp.status_code == 422

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('message') == 'Only refresh tokens are allowed.'
        assert resp_data.get('category') == 'error'
        assert 'access_token' not in resp_data.get('data') and 'refresh_token' not in resp_data.get('data')

    @patch('webapp.tasks.email.send_account_activation_email', Mock())
    def test_resend_confirmation(self, client, user, access_token):
        resp = client.get('/auth/resend-confirmation', headers={'Authorization': f'Bearer {access_token}'})
        assert resp.status_code == 200

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('message') == 'A new confirmation email has been sent to you.'
        assert resp_data.get('category') == 'success'

    def test_confirm_account(self, client, user):
        token = user.generate_jwt_token(expire_time=5)
        resp = client.post('/auth/confirm', json={'token': token})
        assert resp.status_code == 200

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('message') == 'Account confirmed successfully.'
        assert resp_data.get('category') == 'success'

        resp = client.post('/auth/confirm', json={'token': 'invalid'})
        assert resp.status_code == 404

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('message') == 'The confirmation link is invalid or has expired.'
        assert resp_data.get('category') == 'error'

    @patch('webapp.tasks.email.send_reset_password_email', Mock())
    def test_reset_password_email(self, client, user):
        resp = client.post('/auth/reset-password/email', json={'email': user.email})
        assert resp.status_code == 200

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('message') == 'Email was send successfully.'
        assert resp_data.get('category') == 'success'

    def test_reset_password_sett_new_password(self, client, user):
        new_password = '1234abcD'
        token = user.generate_jwt_token(expire_time=5)
        resp = client.post('/auth/reset-password', json={
            'token': token,
            'password': new_password,
            'password_confirm': new_password
        })
        assert resp.status_code == 200

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('message') == 'Password has been reset successfully.'
        assert resp_data.get('category') == 'success'
        assert user.check_password(new_password)

        resp = client.post('/auth/reset-password', json={
            'token': 'invalid',
            'password': '4321Abcd',
            'password_confirm': '4321Abcd'
        })
        assert resp.status_code == 404

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('message') == 'The confirmation link is invalid or has expired.'
        assert resp_data.get('category') == 'error'

        assert user.check_password(new_password)

    def test_change_password(self, client, user, access_token):
        new_password = '1234abcD'
        resp = client.post('/auth/change-password', json={
            'old_password': 'Jofken35',
            'password': new_password,
            'password_confirm': new_password
        }, headers={'Authorization': f'Bearer {access_token}'})
        assert resp.status_code == 200

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('message') == 'Password has been changed successfully.'
        assert resp_data.get('category') == 'success'
        assert user.check_password(new_password)

        resp = client.post('/auth/change-password', json={
            'old_password': 'fake',
            'password': new_password,
            'password_confirm': new_password
        }, headers={'Authorization': f'Bearer {access_token}'})
        assert resp.status_code == 401

        resp_data = json.loads(resp.data.decode('utf-8'))
        assert resp_data.get('message') == 'Invalid current password.'
        assert resp_data.get('category') == 'error'

        assert user.check_password(new_password)
