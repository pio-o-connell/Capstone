import os
import django
from django.template import TemplateSyntaxError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.template.loader import get_template

try:
    get_template('accounts/password_reset_form.html')
    print('TEMPLATE OK')
except TemplateSyntaxError as e:
    print('TEMPLATE SYNTAX ERROR:')
    raise
