"""Contains views for auth blueprint."""

from flask import render_template, redirect, url_for, flash, request, current_app
from flask.views import View
from flask_login import login_user, logout_user, current_user, login_required

from .forms import (RegistrationForm, LoginForm, ResetPasswordEmailForm, ResetPasswordCredentialsForm,
                    AccountUpdateForm, DeleteAccountForm, ChangePasswordForm)
from .models import User
from .utils import redirect_authenticated_users
from ..utils import Blueprint


auth_blueprint = Blueprint('auth',  __name__, template_folder='templates',
                           static_folder='static', static_url_path='/static/auth')


@auth_blueprint.class_route('/register', 'register')
class Register(View):
    """Adds new user."""
    init_every_request = False
    methods = ["GET", "POST"]
    template = 'register.html'
    decorators = [redirect_authenticated_users]

    def dispatch_request(self):
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = User.generate_password_hash(form.password.data)
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            user.save_to_db()
            current_app.logger.info('%s was created.', user)
            from .tasks import send_account_activation_email  # pylint: disable=import-outside-toplevel
            send_account_activation_email.delay(user.id)
            login_user(user)
            flash('User account was created successfully.', 'success')
            return redirect(url_for('auth.unconfirmed'))
        return render_template(self.template, form=form)


@auth_blueprint.class_route('/login', 'login')
class Login(View):
    """Logins user."""
    init_every_request = False
    methods = ["GET", "POST"]
    template = 'login.html'
    decorators = [redirect_authenticated_users]

    def dispatch_request(self):
        form = LoginForm()
        if form.validate_on_submit():
            user = User.find_by_email(form.email.data)
            if user:
                if user.check_password(form.password.data):
                    login_user(user, remember=form.remember.data)
                    current_app.logger.info('%s was logged in.', user)
                    if current_user.is_authenticated and not current_user.active:
                        return redirect(url_for('auth.unconfirmed'))
                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    return redirect(url_for('service.home'))
                current_app.logger.info('%s passed invalid password.', user)
            else:
                current_app.logger.info('User with %s mail does not exist.', form.email.data)
            flash('Invalid email or password!', 'error')
        return render_template(self.template, form=form)


@auth_blueprint.class_route('/logout', 'logout')
class Logout(View):
    """Logouts user."""
    init_every_request = False
    methods = ['GET']
    template = 'logout.html'
    decorators = [login_required]

    def dispatch_request(self):
        user_label = str(current_user)
        logout_user()
        current_app.logger.info('%s was logged out.', user_label)
        return render_template(self.template)


@auth_blueprint.class_route('/unconfirmed', 'unconfirmed')
class Unconfirmed(View):
    """Informs about unconfirmed account."""
    init_every_request = False
    methods = ["GET"]
    template = 'unconfirmed.html'
    decorators = [login_required]

    def dispatch_request(self):
        if current_user.active:
            flash('You have already confirmed your account.', 'warning')
            current_app.logger.warning('%s with confirmed account has visit unconfirmed page.', current_user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('service.home')
        return render_template(self.template)


@auth_blueprint.class_route('/confirm/<token>', 'activate_account')
class ActivateAccount(View):
    """Confirms user's account."""
    init_every_request = False
    methods = ["GET"]

    def dispatch_request(self, token: str):  # pylint: disable=arguments-differ
        user = User.verify_jwt_token(token)
        if user:
            user.active = True
            user.save_to_db()
            current_app.logger.info('%s has confirmed account.', user)
            flash('You have confirmed your account.', 'success')
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            return redirect(url_for('service.home'))
        current_app.logger.warning('%s has used expired link to confirm account.', user)
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('auth.unconfirmed'))


@auth_blueprint.class_route('/resend-confirmation', 'resend_confirmation')
class ResendConfirmation(View):
    """Resends email with link to confirm account."""
    init_every_request = False
    methods = ["GET"]
    decorators = [login_required]

    def dispatch_request(self):
        if current_user.active:
            current_app.logger.warning('%s with confirmed account has request confirmation resending.', current_user)
            flash('You have already confirmed your account.', 'info')
            return redirect(url_for('service.home'))
        from .tasks import send_account_activation_email  # pylint: disable=import-outside-toplevel
        send_account_activation_email.delay(current_user.id)
        current_app.logger.info('Email with confirmation link was send to %s.', current_user)
        flash('A new confirmation email has been sent to you.', 'info')
        return redirect(url_for('auth.unconfirmed'))


@auth_blueprint.class_route('/account', 'account')
class Account(View):
    """Shows user's profile."""
    init_every_request = False
    methods = ["GET"]
    template = 'account.html'
    decorators = [login_required]

    def dispatch_request(self):
        return render_template(self.template)


@auth_blueprint.class_route('/account/update', 'account_update')
class AccountUpdate(View):
    """Updates user's account."""
    init_every_request = False
    methods = ["GET", "POST"]
    template = 'account_update.html'
    decorators = [login_required]

    def dispatch_request(self):
        form = AccountUpdateForm()
        if form.validate_on_submit():
            user_label = str(current_user)
            current_app.logger.info('%s requests account update.', user_label)
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.save_to_db()
            current_app.logger.info('%s account has been updated with data: username=%s, email=%s.', user_label)
            flash('Your account has been updated successfully!', 'success')
            return redirect(url_for('auth.account'))
        if request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
        return render_template(self.template, form=form)


@auth_blueprint.class_route('/account/delete', 'account_delete')
class AccountDelete(View):
    """Delete user."""
    init_every_request = False
    methods = ["GET", "POST"]
    template = 'account_delete.html'
    decorators = [login_required]

    def dispatch_request(self):
        form = DeleteAccountForm()
        if form.validate_on_submit():
            current_user.delete_from_db()
            user_label = current_user
            current_app.logger.info('%s account has been deleted.', user_label)
            logout_user()
            flash('Your account has been deleted successfully.', 'success')
            return redirect(url_for('auth.login'))
        return render_template(self.template, form=form)


@auth_blueprint.class_route('/account/change-password', 'account_change_password')
class AccountChangePassword (View):
    """Changes user's password."""
    init_every_request = False
    methods = ["GET", "POST"]
    template = 'account_change_password.html'
    decorators = [login_required]

    def dispatch_request(self):
        form = ChangePasswordForm()
        if form.validate_on_submit():
            hashed_password = User.generate_password_hash(form.new_password.data)
            current_user.password = hashed_password
            current_user.save_to_db()
            current_app.logger.info('%s changed password.', current_user)
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('auth.account'))
        return render_template(self.template, form=form)


@auth_blueprint.class_route('/reset-password', 'send_reset_password_link')
class SendResetPasswordLink(View):
    """Sends email with link to reset password."""
    init_every_request = False
    methods = ["GET", "POST"]
    template = 'send_reset_password_link.html'
    decorators = [redirect_authenticated_users]

    def dispatch_request(self):
        form = ResetPasswordEmailForm()
        if form.validate_on_submit():
            from .tasks import send_reset_password_email  # pylint: disable=import-outside-toplevel
            send_reset_password_email.delay(form.email.data)
            current_app.logger.info('User with email %s has requested email with link to reset password.',
                                    form.email.data)
            flash('A reset password email has been sent to you.', 'info')
        return render_template(self.template, form=form)


@auth_blueprint.class_route('/reset-password/<token>', 'reset_password')
class ResetPassword(View):
    """Reset user's passwords."""
    init_every_request = False
    methods = ["GET", "POST"]
    template = 'reset_password.html'

    def dispatch_request(self, token):  # pylint: disable=arguments-differ
        user = User.verify_jwt_token(token)
        if not user:
            current_app.logger.warning('%s has used expired link to reset password.', user)
            flash('The confirmation link is invalid or has expired.', 'error')
            return redirect(url_for('auth.login'))
        form = ResetPasswordCredentialsForm()
        if form.validate_on_submit():
            user.password = User.generate_password_hash(form.password.data)
            user.save_to_db()
            current_app.logger.info('%s has has reset password.', user)
            flash('Your password has been reset.', 'success')
            return redirect(url_for('auth.login'))
        return render_template(self.template, form=form)
