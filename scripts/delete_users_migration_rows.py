import os
import sys
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.db.migrations.recorder import MigrationRecorder
from django.db import connection

rec = MigrationRecorder(connection)
qs = rec.migration_qs.filter(app='users')
count = qs.count()
qs.delete()
print(f"Deleted {count} rows for app 'users' from django_migrations")
