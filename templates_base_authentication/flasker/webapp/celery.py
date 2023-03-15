"""Creates celery instance for flasker app."""

from celery import Celery
from flask import Flask

from .app import create_app


def create_celery(app: Flask = None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name)
    celery.conf.update(app.config.get('CELERY_CONFIG', {}))
    TaskBase = celery.Task

    class ContextTask(TaskBase):  # pylint: disable=too-few-public-methods
        """Creates task with current app context."""
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery_app = create_celery()
