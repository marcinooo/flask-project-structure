import os
from pathlib import Path

# Secret key
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

# Root project directory
BASEDIR = Path(__file__).parent.absolute() / '..'

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
