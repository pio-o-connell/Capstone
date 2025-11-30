import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
qs = User.objects.filter(username__startswith='testuser_')
print('test users found:', qs.count())
for u in qs:
    print(u.username, 'active=', u.is_active)
