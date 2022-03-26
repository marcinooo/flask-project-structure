import os
import redis
from flask import Flask, render_template
from pathlib import Path
from dotenv import load_dotenv


def create_app() -> Flask:
    flask_env = os.environ.get('FLASK_ENV')
    if flask_env == 'DEVELOPMENT':
        env_file = Path(__file__).parent.absolute() / '..' / 'environment' / '.env.development'
    elif flask_env == 'PRODUCTION':
        env_file = Path(__file__).parent.absolute() / '..' / 'environment' / '.env.production'
    elif flask_env == 'TESTING':
        env_file = Path(__file__).parent.absolute() / '..' / 'environment' / '.env.testing'
    else:
        raise NotImplemented('Please set "FLASK_ENV" variable to "DEVELOPMENT" or "PRODUCTION", or "TESTING".')

    load_dotenv(env_file)

    config = Path(__file__).parent.absolute() / '..' / 'config' / 'default.py'
    template_folder = Path(__file__).parent.absolute() / 'templates'

    app = Flask(__name__, template_folder=template_folder, instance_relative_config=True)
    app.config.from_pyfile(config)

    cache = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])

    @app.route('/')
    def hello_world():
        name = 'Marcin'
        return render_template('index.html', name=name)

    @app.route('/set_price/<int:price>')
    def set_price(price):
        cache.set("price", price)
        return f"Price set to {price}"

    @app.route('/get_price')
    def get_price():
        price = int(cache.get("price"))
        return f"The price is {price}."

    return app
