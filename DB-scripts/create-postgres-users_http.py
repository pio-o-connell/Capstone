"""Wrapper to run `DB-scripts/create_users_http.py` in a safe/fake-HTTP dry-run.

This inserts a fake `requests` module that logs intended HTTP requests instead of performing them,
so you can see what would be posted to the running site without changing any remote state.

Usage (dry-run):
  .venv\Scripts\python.exe DB-scripts\create-postgres-users_http.py

Note: This does not contact any web server.
"""
from pathlib import Path
import os
import sys
import runpy
import types
from dataclasses import dataclass, field
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Default remote DB URL (for completeness; create_users_http talks to a web server, not DB directly)
DEFAULT_DATABASE_URL = (
    "postgresql://neondb_owner:npg_Jdzr3MEnZiN2@"
    "ep-patient-mountain-agw6c8sf.c-2.eu-central-1.aws.neon.tech/"
    "oil_shun_widow_111921"
)


@dataclass
class FakeResponse:
    status_code: int = 200
    text: str = ""
    raw: Any = None


@dataclass
class RecordedRequest:
    method: str
    url: str
    data: Any = None
    files: Any = None
    headers: Dict[str, str] = field(default_factory=dict)


class FakeSession:
    def __init__(self):
        self.recorded: List[RecordedRequest] = []

    def get(self, url, timeout=None):
        self.recorded.append(RecordedRequest('GET', url))
        # Return a page with a fake CSRF token when registration/profile/login endpoints are requested
        sample_html = "<input type='hidden' name='csrfmiddlewaretoken' value='fake-token-123' />"
        return FakeResponse(status_code=200, text=sample_html)

    def post(self, url, data=None, files=None, headers=None, allow_redirects=True, timeout=None):
        self.recorded.append(RecordedRequest('POST', url, data=data, files=files, headers=headers or {}))
        # pretend successful post/redirect
        return FakeResponse(status_code=302, text='')


class FakeRequestsModule(types.SimpleNamespace):
    def __init__(self):
        super().__init__()
        self._session = FakeSession()

    def Session(self):
        return self._session


def main():
    # Make sure wrappers point at the intended remote DB (if other parts read it)
    os.environ.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL', DEFAULT_DATABASE_URL))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # Install fake requests module into sys.modules so the target script imports it
    fake_requests = FakeRequestsModule()
    sys.modules['requests'] = fake_requests

    script_path = str(Path(__file__).resolve().parent / 'create_users_http.py')
    print('Running create_users_http.py in safe dry-run (no network calls will be made)')
    runpy.run_path(script_path, run_name='__main__')

    # After run, print recorded session activity (if any)
    sess = fake_requests._session
    print('\n--- Recorded HTTP activity (dry-run) ---')
    for r in sess.recorded:
        print(r.method, r.url)
        if r.data:
            print('  data keys:', list(r.data.keys()) if isinstance(r.data, dict) else type(r.data))
    print('--- End recorded activity ---')


if __name__ == '__main__':
    main()
