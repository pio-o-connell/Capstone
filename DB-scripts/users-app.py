# users/apps.py

# users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals


And in settings.py:

INSTALLED_APPS = [
    ...
    'users.apps.UsersConfig',
]