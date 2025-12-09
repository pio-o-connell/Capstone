#!/usr/bin/env python
"""Create sample posts and comments for local development.
Run with: python scripts/create_sample_data.py
"""
from pathlib import Path
import sys
import os

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Some installations of `bleach` don't accept the `styles` kw used by
# `django_summernote`. Monkeypatch `bleach.clean` to ignore `styles` if
# present so our development script can create sample content.
try:
    import bleach
    _bleach_clean = bleach.clean
    def _clean(*args, **kwargs):
        kwargs.pop('styles', None)
        return _bleach_clean(*args, **kwargs)
    bleach.clean = _clean
except Exception:
    # If bleach isn't available or fails, proceed; summernote fields may still error.
    pass

import django
django.setup()

from django.contrib.auth import get_user_model
from blog.models import Post, Comment

User = get_user_model()

# Try to use existing admin if present, otherwise create a simple user
author = None
try:
    author = User.objects.filter(username='admin').first()
except Exception:
    pass

if not author:
    author, created = User.objects.get_or_create(
        username='sample_author',
        defaults={'email': 'author@example.local'}
    )
    if created:
        author.set_password('password')
        author.is_staff = False
        author.save()

print('Using author:', author.username)

sample_posts = [
    ("Quick Lawn Care Tips", "Short tips for keeping your lawn healthy."),
    ("Hedge Trimming Guide", "When and how to trim your hedges for best results."),
    ("Scarifying & Aeration", "Why scarifying and aeration matter for lawn health."),
]

created = []
for title, excerpt in sample_posts:
    p = Post.objects.create(
        author=author,
        title=title,
        content=excerpt + "\n\nThis is sample content created for development.",
        excerpt=excerpt,
        status='published',
    )
    created.append(p)
    print('Created post:', p.title, 'id=', p.id)

# Add comments
for p in created:
    c1 = Comment.objects.create(post=p, author=author, name=author.username, email=author.email, content='Great post — thanks for sharing!')
    c2 = Comment.objects.create(post=p, author=None, name='Guest', email='guest@example.local', content='Nice tips — very helpful.')
    print('  Added comments:', c1.id, c2.id)

print('Sample data creation complete.')
