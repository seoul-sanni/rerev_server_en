from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

CORS_ALLOWED_ORIGINS = [
    'http://localhost:4000',
    'https://rerev.kr',
    'https://www.rerev.kr',
    'https://en.rerev.kr',
    'https://alpha.rerev.kr',
    'https://beta.rerev.kr',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:4000',
    'https://rerev.kr',
    'https://www.rerev.kr',
    'https://en.rerev.kr',
    'https://alpha.rerev.kr',
    'https://beta.rerev.kr',
]

WSGI_APPLICATION = 'server.wsgi.deploy.application'

# Celery
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'