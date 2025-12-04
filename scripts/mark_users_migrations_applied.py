import os
import sys
from pathlib import Path

# ensure project importable
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

rec = MigrationRecorder(connection)
existing = set(rec.migration_qs.values_list('app', 'name'))
need = [
    ('users', '0001_initial'),
    ('users', '0002_remove_bloggerprofile_bio_and_more'),
]
for app, name in need:
    if (app, name) in existing:
        print(f"Already recorded: {app} {name}")
    else:
        rec.record_applied(app, name)
        print(f"Marked applied: {app} {name}")
print('Done')
