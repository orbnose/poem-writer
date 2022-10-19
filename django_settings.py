import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INSTALLED_APPS = [
            'db',
        ]

DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite3'
            }
        }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECRET_KEY = '!dghyttt--=hc99-!vy_v(t61v$nc#z+)dw@b_+^0lhea60q&l'