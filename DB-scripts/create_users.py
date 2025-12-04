r"""Create 20 users with profiles for local development.

Place this file in `DB-scripts/` and run from project root with the project's venv active:

& .\.venv\Scripts\Activate.ps1
python .\DB-scripts\create_users.py

Behaviour:
- Creates 1 administrator user (username: admin) and sets a password if not present.
- Creates customers, bloggers and guests to total 20 users.
- Assigns avatars according to the rules below. If Cloudinary is configured this script will
  attempt to upload the local images and use the uploaded public_id. Otherwise the script
  will write the local file path string into the avatar field (development convenience).

Avatar mapping (files must be in the same `DB-scripts` folder):
- registered customer: business.jpg
- blogger: trippy.jpg
- visiting guest: profile2.jpg
- administrator: sysAdmin.jpg

All profile fields (phone and address) are filled with sample data.
"""

from pathlib import Path
import os
import sys
import json

# Ensure project root is importable and configure Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from users.models import CustomerProfile, BloggerProfile
from django.utils import timezone

User = get_user_model()

HERE = Path(__file__).resolve().parent
# local image files (relative to DB-scripts folder)
IMAGES = {
    'customer': HERE / 'business.jpg',
    'blogger': HERE / 'trippy.jpg',
    'guest': HERE / 'profile2.jpg',
    'admin': HERE / 'sysAdmin.jpg',
}

# Try to import cloudinary uploader if available
_cloudinary = None
try:
    import cloudinary.uploader as _uploader
    _cloudinary = _uploader
except Exception:
    _cloudinary = None


# If cloudinary_uploads.json exists, prefer mapping from that file instead of re-uploading.
MAPPING_FILE = HERE / 'cloudinary_uploads.json'
_mapping = {}
if MAPPING_FILE.exists():
    try:
        _mapping = json.loads(MAPPING_FILE.read_text())
    except Exception:
        _mapping = {}


def upload_if_possible(path: Path):
    """Upload a local file to Cloudinary if uploader available, else return string path.
    Returns a string suitable to assign to a CloudinaryField in development (public_id or path).
    """
    if not path.exists():
        return str(path)
    # If we have a mapping (from upload_to_cloudinary), prefer that
    rel = str(path.relative_to(BASE_DIR))
    if rel in _mapping:
        entry = _mapping[rel]
        return entry.get('public_id') or entry.get('url') or str(path)
    # Otherwise, try uploader if available
    if _cloudinary:
        try:
            res = _cloudinary.upload(str(path))
            return res.get('public_id') or res.get('secure_url') or str(path)
        except Exception as e:
            print('Cloudinary upload failed for', path, '->', e)
            return str(path)
    return str(path)


# Ensure admin exists and has a password
admin, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.local'})
if created:
    admin.set_password('AdminPass123!')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print('Created admin user with username=admin')
else:
    # Make sure flags and password exist (do not overwrite if already set by you)
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print('Admin user exists; ensured is_staff/is_superuser flags')

# Attach admin profile/avatar
admin_avatar = upload_if_possible(IMAGES['admin'])
CustomerProfile.objects.update_or_create(user=admin, defaults={
    'avatar': admin_avatar,
    'phone': '000-000-0000',
    'address': 'System Administrator',
})

# Create sample users: target total 20 incl admin
TOTAL = 20
created_users = [admin]

# Decide distribution: remaining users
remaining = TOTAL - 1
# e.g., customers 8, bloggers 6, guests remaining
num_customers = max(1, remaining // 3)
num_bloggers = max(1, remaining // 3)
num_guests = remaining - (num_customers + num_bloggers)

print('Creating users: customers=%d, bloggers=%d, guests=%d' % (num_customers, num_bloggers, num_guests))

counter = 1

def safe_username(prefix, n):
    return f"{prefix}{n:02d}"

# Create Customers
for i in range(1, num_customers + 1):
    username = safe_username('customer', i)
    user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.local'})
    if created:
        user.set_password('Password123!')
        user.is_customer = True
        user.is_blogger = False
        user.save()
    # upload avatar or use path
    avatar_val = upload_if_possible(IMAGES['customer'])
    CustomerProfile.objects.update_or_create(user=user, defaults={
        'avatar': avatar_val,
        'phone': f'+44 7700 {1000 + i}',
        'address': f'123 Customer St, Unit {i}',
    })
    created_users.append(user)

# Create Bloggers
for i in range(1, num_bloggers + 1):
    username = safe_username('blogger', i)
    user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.local'})
    if created:
        user.set_password('Password123!')
        user.is_customer = False
        user.is_blogger = True
        user.save()
    else:
        user.is_blogger = True
        user.save()
    avatar_val = upload_if_possible(IMAGES['blogger'])
    BloggerProfile.objects.update_or_create(user=user, defaults={
        'avatar': avatar_val,
        'about': f'I am {username}, writing about gardening and outdoor spaces.',
    })
    created_users.append(user)

# Create Guests (still create accounts to simulate visitors)
for i in range(1, num_guests + 1):
    username = safe_username('guest', i)
    user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.local'})
    if created:
        user.set_password('Password123!')
        user.is_customer = False
        user.is_blogger = False
        user.save()
    avatar_val = upload_if_possible(IMAGES['guest'])
    # give guests a customer-like profile for demo
    CustomerProfile.objects.update_or_create(user=user, defaults={
        'avatar': avatar_val,
        'phone': f'+44 7700 {2000 + i}',
        'address': f'Guest House {i}',
    })
    created_users.append(user)

print(f'Total users now in script list: {len(created_users)}')
print('Sample users created/updated:')
for u in created_users:
    print(' -', u.username, 'customer=', getattr(u, 'is_customer', None), 'blogger=', getattr(u, 'is_blogger', None))

print('Done.')
