import os, sys
# Ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from django.urls import resolve, Resolver404
try:
    match = resolve('/')
    print('Matched:', match)
    print('func:', match.func)
    print('args:', match.args)
    print('kwargs:', match.kwargs)
except Resolver404:
    print('No match (Resolver404)')
