"""Contains functions executed by celery worker."""

from flask import current_app, render_template
from ..celery import celery_app

from .models import User


@celery_app.task(bind=True)
def send_account_activation_email(_, user_id: int) -> None:
    """
    Sends email with private link to activate account.

    :param user_id: user id
    :return: None
    """
    user = User.find_by_id(user_id)
    token = user.generate_jwt_token(expire_time=current_app.config['ACCOUNT_ACTIVATION_LINK_EXPIRE_TIME'])
    mail_artifacts = {
        'subject': '[Flasker] Activate Your Account',
        'sender': current_app.config['MAIL_OFFICIAL_SITE_ADDRESS'],
        'recipients': [user.email],
        'text_body': render_template('activate_account_email_template.txt', user=user, token=token),
        'html_body': render_template('activate_account_email_template.html', user=user, token=token)
    }
    print(f'[*] Sending email: {mail_artifacts}')  # mock of sending email


@celery_app.task(bind=True)
def send_reset_password_email(_, user_email: str) -> None:
    """
    Sends email with private link to reset password.

    :param user_email: user email
    :return: None
    """
    user = User.find_by_email(user_email)
    if user is None:
        return
    token = user.generate_jwt_token(expire_time=current_app.config['RESET_PASSWORD_LINK_EXPIRE_TIME'])
    mail_artifacts = {
        'subject': '[Flasker] Reset Your Account Password',
        'sender': current_app.config['MAIL_OFFICIAL_SITE_ADDRESS'],
        'recipients': [user.email],
        'text_body': render_template('reset_password_email_template.txt', user=user, token=token),
        'html_body': render_template('reset_password_email_template.html', user=user, token=token)
    }
    print(f'[*] Sending email: {mail_artifacts}')  # mock of sending email
