import click
from flask.cli import FlaskGroup
from flask_migrate import Migrate

from webapp import create_app, db, users_models


app = create_app()
migrate = Migrate(app, db)
cli = FlaskGroup(app)


@app.shell_context_processor
def make_shell_context() -> dict:
    return dict(app=app, db=db, User=users_models.User)


@cli.command("create_db")
def create_db():  # TODO: it should be build as default
    db.create_all()
    db.session.commit()


@cli.command("drop_db")
def drop_db():
    db.drop_all()


@cli.command('create_user')
@click.argument('username')
@click.argument('email')
@click.argument('password')
def create_user(username, email, password):
    if users_models.User.find_by_username(username):
        print(f'User with username="{username}" already exists.')
        return
    if users_models.User.find_by_email(email):
        print(f'User with email="{email}" already exists.')
        return
    hashed_password = users_models.User.generate_password_hash(password)
    user = users_models.User(username=username, email=email, password=hashed_password)
    user.save_to_db()


if __name__ == "__main__":
    cli()
