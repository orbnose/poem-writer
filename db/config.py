import os
import django

def configureDjango():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'django_settings'
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
    django.setup()

