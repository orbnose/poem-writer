import os
import django

def configureDjango():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'poem.django_settings'
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "poem.django_settings")
    django.setup()

