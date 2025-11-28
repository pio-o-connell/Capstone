import os
import django
from django.template import TemplateSyntaxError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    print('DJANGO_SETTINGS_MODULE not set')

django.setup()

from django.template.loader import get_template

try:
    get_template('accounts/register.html')
    print('register.html OK')
except TemplateSyntaxError as e:
    print('TEMPLATE SYNTAX ERROR:')
    raise
