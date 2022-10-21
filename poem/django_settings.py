# Settings for running in standalone django orm

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INSTALLED_APPS = [
            'poem',
        ]

DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite3'
            }
        }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
