import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from blog.models import Post, Comment
print('Total posts:', Post.objects.count())
print('Total comments:', Comment.objects.count())
print('\nRecent posts and comment counts:')
for p in Post.objects.all()[:10]:
    print(p.title, 'by', getattr(p.author,'username',None), 'comments=', p.comments.count())
