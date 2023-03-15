import click
from flask.cli import FlaskGroup
from flask_migrate import Migrate

from webapp import create_app, db, auth_models


app = create_app()
migrate = Migrate(app, db)
cli = FlaskGroup(app)


@app.shell_context_processor
def make_shell_context() -> dict:
    return dict(app=app, db=db, User=auth_models.User, Role=auth_models.Role)


@cli.command("create_db")
def create_db():  # TODO: it should be build as default
    db.create_all()
    db.session.commit()

    auth_models.Role.save_all_to_db()


@cli.command("drop_db")
def drop_db():
    db.drop_all()


@cli.command('create_user')
@click.argument('username')
@click.argument('email')
@click.argument('password')
def create_user(username, email, password):
    if auth_models.User.find_by_username(username):
        print(f'User with username="{username}" already exists.')
        return
    if auth_models.User.find_by_email(email):
        print(f'User with email="{email}" already exists.')
        return
    hashed_password = auth_models.User.generate_password_hash(password)
    user = auth_models.User(username=username, email=email, password=hashed_password)
    user.save_to_db()


if __name__ == "__main__":
    cli()
