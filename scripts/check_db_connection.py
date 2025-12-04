import os
import sys
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings
from django.db import connections

print('DATABASES["default"] from settings:')
import json
print(json.dumps(settings.DATABASES.get('default', {}), indent=2))

conn = connections['default']
try:
    with conn.cursor() as cur:
        try:
            cur.execute('SELECT version()')
            ver = cur.fetchone()
        except Exception as e:
            ver = ('error', str(e))
        try:
            cur.execute("SELECT inet_server_addr(), inet_client_addr()")
            addrs = cur.fetchone()
        except Exception as e:
            addrs = ('error', str(e))
    print('\nDB server version:')
    print(ver)
    print('\ninet_server_addr(), inet_client_addr():')
    print(addrs)
except Exception as e:
    print('\nFailed to query DB:', e)
    print('Connection settings dict:')
    try:
        print(json.dumps(conn.settings_dict, indent=2))
    except Exception:
        print(conn.settings_dict)
