import os
import sys
import json
from pathlib import Path

# Ensure project root is on sys.path so `config` settings module can be imported
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.db import connections

c = connections['default']
with c.cursor() as cur:
    cur.execute('SELECT id, app, name, applied FROM django_migrations ORDER BY id')
    rows = cur.fetchall()

def fmt(x):
    try:
        return x.isoformat()
    except Exception:
        return str(x)

out = []
for r in rows:
    out.append({'id': r[0], 'app': r[1], 'name': r[2], 'applied': fmt(r[3])})

print(json.dumps(out, indent=2))
