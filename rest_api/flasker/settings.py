import os
from datetime import timedelta


SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

FLASK_DEBUG = str(os.environ.get('FLASK_DEBUG')).lower() in ('true', '1', 't')

TESTING = str(os.environ.get('FLASK_TESTING')).lower() in ('true', '1', 't')

ACCOUNT_ACTIVATION_LINK_EXPIRE_TIME = 3 * 24 * 60 * 60  # 3 days

RESET_PASSWORD_LINK_EXPIRE_TIME = 1 * 60 * 60  # 1 hour

ADMINISTRATOR_MAILS = ['admin@fake-mail.com']

MAIL_OFFICIAL_SITE_ADDRESS = 'flasker@fake-mail.com'


# Server name
SERVER_NAME = os.environ.get('SERVER_NAME')


# Database
DATABASE_URI = os.environ.get('DATABASE_URI')

if DATABASE_URI:
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
else:
    SQLALCHEMY_DATABASE_USER = os.environ.get('SQLALCHEMY_DATABASE_USER')
    SQLALCHEMY_DATABASE_PASSWORD = os.environ.get('SQLALCHEMY_DATABASE_PASSWORD')
    SQLALCHEMY_DATABASE_HOST = os.environ.get('SQLALCHEMY_DATABASE_HOST')
    SQLALCHEMY_DATABASE_PORT = os.environ.get('SQLALCHEMY_DATABASE_PORT')
    SQLALCHEMY_DATABASE_DB = os.environ.get('SQLALCHEMY_DATABASE_DB')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{SQLALCHEMY_DATABASE_USER}:{SQLALCHEMY_DATABASE_PASSWORD}' \
                              f'@{SQLALCHEMY_DATABASE_HOST}:{SQLALCHEMY_DATABASE_PORT}/{SQLALCHEMY_DATABASE_DB}'


# Redis
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'


ACCESS_EXPIRES = timedelta(minutes=20)
REFRESH_EXPIRES = timedelta(days=2)


# Celery
CELERY_CONFIG = {
    'broker_url': REDIS_URL,
    'result_backend': REDIS_URL,
    'include': [
        'webapp.tasks.email',
    ]
}

if TESTING:
    # WFT form extension
    WTF_CSRF_METHODS = []
    WTF_CSRF_ENABLED = False
    # Celery
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    BROKER_BACKEND = 'memory'
