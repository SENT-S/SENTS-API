# config/development.py
from .base_config import *

SQLALCHEMY_DATABASE_URI = os.getenv('DEVELOPMENT_DB_URL')
