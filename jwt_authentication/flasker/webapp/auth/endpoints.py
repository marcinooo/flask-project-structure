"""Contains endpoints of auth blueprint."""

from flask import Blueprint, current_app
from flask_jwt_extended import (create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt)

from ..schemas.auth import (UserLoginSchema, UserRegisterSchema, ConfirmTokenSchema, PasswordResetEmailSchema,
                            PasswordResetSchema, PasswordChangeSchema)
from ..models.users import User
from ..app import bcrypt, redis
from ..utils import use_schema, error_response, success_response


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route("/auth/register", methods=["POST"])
@use_schema
def register(body: UserRegisterSchema):
    """Creates new user."""
    user = User(**body.dict(exclude={'password', 'password_confirm'}))
    user.password = User.generate_password_hash(body.password)
    user.save_to_db()
    from ..tasks.email import send_account_activation_email  # pylint: disable=import-outside-toplevel
    send_account_activation_email.delay(user.id)
    return success_response(message=f'User {user.username} was created successfully.', http_code=201, data={})


@auth_blueprint.route("/auth/login", methods=["POST"])
@use_schema
def login(body: UserLoginSchema):
    """Validates credentials and return access and refresh token."""
    user = User.find_by_email(email=body.email)
    if user and user.check_password(body.password):
        user_id = str(user.id)
        access_token = create_access_token(identity=user_id, expires_delta=current_app.config['ACCESS_EXPIRES'],
                                           fresh=True)
        refresh_token = create_refresh_token(identity=user_id, expires_delta=current_app.config['REFRESH_EXPIRES'])
        return success_response(message='Login successful.', http_code=200,
                                data={'access_token': access_token, 'refresh_token': refresh_token})
    return error_response(message='Invalid credentials.', http_code=401, data={})


@auth_blueprint.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refreshes access token."""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id, expires_delta=current_app.config['ACCESS_EXPIRES'],
                                       fresh=False)
    refresh_token = create_refresh_token(identity=user_id, expires_delta=current_app.config['REFRESH_EXPIRES'])
    jti = get_jwt()["jti"]
    redis.set(jti, "", ex=current_app.config['REFRESH_EXPIRES'])
    return success_response(message='Refresh successful.', http_code=200,
                            data={'access_token': access_token, 'refresh_token': refresh_token})


@auth_blueprint.route("/auth/revoke-access-token", methods=["DELETE"])
@jwt_required()
def revoke_access_token():
    """Revokes access tokens."""
    jti = get_jwt()["jti"]
    redis.set(jti, "", ex=current_app.config['ACCESS_EXPIRES'])
    return success_response(message='Access token revoked successfully.', http_code=200, data={})


@auth_blueprint.route("/auth/revoke-refresh-token", methods=["DELETE"])
@jwt_required(refresh=True)
def revoke_refresh_token():
    """Revokes refresh tokens."""
    jti = get_jwt()["jti"]
    redis.set(jti, "", ex=current_app.config['REFRESH_EXPIRES'])
    return success_response(message='Refresh token revoked successfully.', http_code=200, data={})


@auth_blueprint.route('/auth/confirm', methods=["POST"])
@use_schema
def confirm(body: ConfirmTokenSchema):
    """Confirms new user account."""
    user = User.verify_jwt_token(body.token)
    if user:
        user.active = True
        user.save_to_db()
        return success_response(message='Account confirmed successfully.', http_code=200, data={})
    return error_response(message='The confirmation link is invalid or has expired.', http_code=404, data={})


@auth_blueprint.route('/auth/resend-confirmation', methods=["GET"])
@jwt_required()
def resend_confirmation():
    """Resends confirmation link to activate new account."""
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)
    if user and user.active:
        return success_response(message='You have already confirmed your account.', http_code=200, data={})
    from ..tasks.email import send_account_activation_email  # pylint: disable=import-outside-toplevel
    send_account_activation_email.delay(user_id)
    return success_response(message='A new confirmation email has been sent to you.', http_code=200, data={})


@auth_blueprint.route("/auth/reset-password/email", methods=["POST"])
@use_schema
def reset_password_email(body: PasswordResetEmailSchema):
    """Sends email with link to reset password."""
    from ..tasks.email import send_reset_password_email  # pylint: disable=import-outside-toplevel
    send_reset_password_email.delay(body.email)
    return success_response(message='Email was send successfully.', http_code=200, data={})


@auth_blueprint.route("/auth/reset-password", methods=["POST"])
@use_schema
def reset_password(body: PasswordResetSchema):
    """Resets user's password."""
    user = User.verify_jwt_token(body.token)
    if not user:
        return error_response(message='The confirmation link is invalid or has expired.', http_code=404, data={})
    user.password = User.generate_password_hash(body.password)
    user.save_to_db()
    return success_response(message='Password has been reset successfully.', http_code=200, data={})


@auth_blueprint.route("/auth/change-password", methods=["POST"])
@jwt_required()
@use_schema
def change_password(body: PasswordChangeSchema):
    """Changes user password."""
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)
    if not bcrypt.check_password_hash(user.password, body.old_password):
        return error_response(message='Invalid current password.', http_code=401, data={})
    user.password = User.generate_password_hash(body.password)
    user.save_to_db()
    return success_response(message='Password has been changed successfully.', http_code=200, data={})
