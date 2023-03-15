"""Contains redis adapter."""

from redis import Redis
from flask import Flask


class RedisManager:
    """Creates Flask extension to manage redis database."""

    def __init__(self, app: Flask = None):
        self.redis = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initializes extension.

        :param app: instance of Flask app
        :return: None
        """
        self.redis = Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], db=0, decode_responses=True)

    def set(self, *args, **kwargs):
        """
        Call set() method of Redis instance.
        :param args: Check Redis's set() method docs.
        :param kwargs: Check Redis's set() method docs.
        :return: Check Redis's set() method docs.
        """
        return self.redis.set(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Call get() method of Redis instance.
        :param args: Check Redis's get() method docs.
        :param kwargs: Check Redis's get() method docs.
        :return: Check Redis's get() method docs.
        """
        return self.redis.get(*args, **kwargs)
