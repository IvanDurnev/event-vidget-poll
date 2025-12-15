import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key")

    STATIC_FOLDER = os.path.join(basedir, 'static')
    TEMPLATES_FOLDER = os.path.join(basedir, 'templates')

    # Postgres
    user = os.environ.get('POSTGRES_USER')
    pw = os.environ.get('POSTGRES_PW')
    url = os.environ.get('POSTGRES_URL')
    db = os.environ.get('POSTGRES_DB')
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{user}:{pw}@{url}/{db}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL")