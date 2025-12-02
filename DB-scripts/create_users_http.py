"""Create users by POSTing to a running Django site.

Usage:
  & .\.venv\Scripts\Activate.ps1
  python .\DB-scripts\create_users_http.py

The script will:
- Try common registration endpoints until one responds with a form (CSRF token present).
- For each user, GET registration page to grab CSRF token, POST username/email/password1/password2.
- Attempt to login and then POST profile data (including avatar file) to common profile endpoints.

Files expected in the same folder (for avatars):
- business.jpg, trippy.jpg, profile2.jpg, sysAdmin.jpg

Notes:
- Requires `requests` package. Install with `pip install requests` in your venv if missing.
- Server must be running at `BASE_URL` (default http://127.0.0.1:8000).
"""

from pathlib import Path
import re
import sys
import time
import json

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

import os

BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:8000')

try:
    import requests
except Exception:
    print('This script requires the `requests` package. Install it in your venv: pip install requests')
    raise
try:
    import tempfile
    import shutil
except Exception:
    pass

CSRF_RE = re.compile(r"name=['\"]csrfmiddlewaretoken['\"] value=['\"](?P<token>[^'\"]+)['\"]")

REG_ENDPOINTS = [
    '/accounts/register/', '/accounts/signup/', '/register/', '/signup/',
    '/accounts/register', '/accounts/signup', '/register', '/signup'
]

LOGIN_ENDPOINTS = ['/accounts/login/', '/accounts/signin/', '/login/', '/signin/']

PROFILE_ENDPOINTS = [
    '/accounts/profile/', '/accounts/profile/edit/', '/profile/', '/profile/edit/',
    '/accounts/settings/profile/', '/users/profile/edit/', '/accounts/edit_profile/',
]

# avatar files mapping
IMAGES = {
    'customer': BASE_DIR / 'business.jpg',
    'blogger': BASE_DIR / 'trippy.jpg',
    'guest': BASE_DIR / 'profile2.jpg',
    'admin': BASE_DIR / 'sysAdmin.jpg',
}

# helper functions

def find_registration_url(session):
    for ep in REG_ENDPOINTS:
        url = BASE_URL.rstrip('/') + ep
        try:
            r = session.get(url, timeout=5)
        except Exception:
            continue
        if r.status_code == 200 and 'csrfmiddlewaretoken' in r.text:
            print('Found registration page at', url)
            return url
    return None


def extract_csrf(html):
    m = CSRF_RE.search(html)
    return m.group('token') if m else None


def try_login(session, username, password):
    for ep in LOGIN_ENDPOINTS:
        url = BASE_URL.rstrip('/') + ep
        try:
            r = session.get(url, timeout=5)
        except Exception:
            continue
        if r.status_code != 200:
            continue
        token = extract_csrf(r.text)
        if not token:
            continue
        data = {'username': username, 'password': password, 'csrfmiddlewaretoken': token}
        headers = {'Referer': url}
        resp = session.post(url, data=data, headers=headers, allow_redirects=True, timeout=10)
        # check if login succeeded by requesting home and searching for Logout or username
        h = session.get(BASE_URL + '/', timeout=5).text
        if 'Logout' in h or username in h:
            return True
    return False


def try_update_profile(session, avatar_path, extra_fields=None):
    files = {}
    data = extra_fields or {}
    if avatar_path and Path(avatar_path).exists():
        try:
            files['avatar'] = open(avatar_path, 'rb')
        except Exception:
            files = {}
    success = False
    for ep in PROFILE_ENDPOINTS:
        url = BASE_URL.rstrip('/') + ep
        try:
            r = session.get(url, timeout=5)
        except Exception:
            continue
        if r.status_code != 200:
            continue
        token = extract_csrf(r.text)
        if not token:
            continue
        data['csrfmiddlewaretoken'] = token
        headers = {'Referer': url}
        try:
            resp = session.post(url, data=data, files=files or None, headers=headers, allow_redirects=True, timeout=10)
        except Exception:
            continue
        if resp.status_code in (200, 302):
            success = True
            break
    if files:
        for f in files.values():
            try:
                f.close()
            except Exception:
                pass
    return success


def create_user_via_registration(session, reg_url, username, email, password):
    # GET page
    r = session.get(reg_url, timeout=5)
    if r.status_code != 200:
        return False, 'GET failed'
    token = extract_csrf(r.text)
    if not token:
        return False, 'no csrf'
    data = {
        'csrfmiddlewaretoken': token,
        'username': username,
        'email': email,
        'password1': password,
        'password2': password,
    }
    headers = {'Referer': reg_url}
    resp = session.post(reg_url, data=data, headers=headers, allow_redirects=True, timeout=10)
    # After POST, check if logged in or can access profile
    home = session.get(BASE_URL + '/', timeout=5).text
    if 'Logout' in home or username in home:
        return True, 'registered and logged in'
    # Some registration views redirect to login; check for successful response code
    if resp.status_code in (200, 302):
        return True, 'posted'
    return False, f'post failed ({resp.status_code})'


def main():
    s = requests.Session()
    # quick check server
    try:
        r = s.get(BASE_URL + '/', timeout=4)
    except Exception as e:
        print('Cannot reach', BASE_URL, '— start your dev server and retry. Error:', e)
        return
    reg_url = find_registration_url(s)
    if not reg_url:
        print('Could not find a registration page; available endpoints tried:', REG_ENDPOINTS)
        return

    # prepare users: 20 total including admin
    total = 20
    users = []
    users.append({'username': 'admin', 'email': 'admin@example.local', 'password': 'AdminPass123!', 'type': 'admin'})
    # remaining
    rem = total - 1
    num_customers = max(1, rem // 3)
    num_bloggers = max(1, rem // 3)
    num_guests = rem - (num_customers + num_bloggers)
    for i in range(1, num_customers + 1):
        users.append({'username': f'customer{i:02d}', 'email': f'customer{i:02d}@example.local', 'password': 'Password123!', 'type': 'customer'})
    for i in range(1, num_bloggers + 1):
        users.append({'username': f'blogger{i:02d}', 'email': f'blogger{i:02d}@example.local', 'password': 'Password123!', 'type': 'blogger'})
    for i in range(1, num_guests + 1):
        users.append({'username': f'guest{i:02d}', 'email': f'guest{i:02d}@example.local', 'password': 'Password123!', 'type': 'guest'})

    print('Will attempt to create', len(users), 'users via', reg_url)

    summary = []
    for u in users:
        print('\nCreating', u['username'], 'type', u['type'])
        ok, msg = create_user_via_registration(s, reg_url, u['username'], u['email'], u['password'])
        if not ok:
            print('  Registration POST failed:', msg)
            # maybe user exists; try to login to attach profile
            logged_in = try_login(s, u['username'], u['password'])
            if not logged_in:
                print('  Could not login as', u['username'], '; skipping profile upload')
                summary.append((u['username'], False, 'register_failed'))
                continue
            else:
                print('  Logged in (user may already exist)')
        else:
            print('  Registration result:', msg)
        # now logged in, attempt to upload avatar/profile
        avatar_file_path = IMAGES.get(u['type'], IMAGES['guest'])
        avatar_file = str(avatar_file_path)
        # If a cloudinary mapping exists, download mapped URL to a temp file for upload
        mapping_file = Path(BASE_DIR) / 'cloudinary_uploads.json'
        if mapping_file.exists():
            try:
                mapping = json.loads(mapping_file.read_text())
                rel = str(avatar_file_path.relative_to(Path(__file__).resolve().parent))
                entry = mapping.get(rel) or mapping.get(str(avatar_file_path))
                if entry and entry.get('url'):
                    # download to temp file
                    r = s.get(entry['url'], stream=True, timeout=10)
                    if r.status_code == 200:
                        tf = tempfile.NamedTemporaryFile(delete=False, suffix='.' + entry['url'].split('.')[-1])
                        with open(tf.name, 'wb') as fh:
                            shutil.copyfileobj(r.raw, fh)
                        avatar_file = tf.name
            except Exception:
                pass
        extra = {}
        if u['type'] == 'blogger':
            extra['about'] = f'I am {u["username"]}, sample blogger.'
        else:
            extra['phone'] = '+44 7700 000000'
            extra['address'] = '123 Demo Street'
        prof_ok = try_update_profile(s, avatar_file, extra_fields=extra)
        print('  Profile update success=', prof_ok)
        summary.append((u['username'], True, 'profile_updated' if prof_ok else 'created_no_profile'))
        # small delay to avoid hammering
        time.sleep(0.5)

    print('\nSummary:')
    for r in summary:
        print(' -', r[0], r[1], r[2])

if __name__ == '__main__':
    main()
