import os

DEBUG = True
ALLOWED_HOSTS = []
SECRET_KEY = '090d2#wtg&q2@o+l%cvc&4)r4x5fr9o#r^qz3%0bemyecshn31'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ac_mediator',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': os.getenv('DOCKER_DB_HOST', '127.0.0.1')
    }
}

BASE_URL = os.getenv('DOCKER_DJANGO_BASE_URL', 'http://localhost:8000')
