import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.template.loader import get_template
print('Loading accounts/login.html...')
get_template('accounts/login.html')
print('OK')
