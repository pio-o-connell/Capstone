import os
import sys
import pathlib
import django
# Ensure project root is on PYTHONPATH so `config` module is importable
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
print('Total users:', User.objects.count())
print('Superusers:', list(User.objects.filter(is_superuser=True).values_list('username', flat=True)))
print('\nSample users:')
for u in User.objects.all()[:20]:
    print(u.username, 'is_customer=', getattr(u, 'is_customer', None), 'is_blogger=', getattr(u, 'is_blogger', None))
