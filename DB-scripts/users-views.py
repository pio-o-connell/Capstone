from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post

def post_list(request):
    posts = Post.objects.filter(status='published')
    return render(request, 'blog/post_list.html', {'posts': posts})

@login_required
def create_post(request):
    if not request.user.is_blogger:
        return redirect('post_list')
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        Post.objects.create(author=request.user, title=title, content=content, status='draft')
        return redirect('post_list')
    return render(request, 'blog/create_post.html')

def request_blogger(request):
    if request.method == 'POST':
        reason = request.POST.get("reason")
        BloggerRequest.objects.create(user=request.user, reason=reason)
        return redirect('dashboard')
    return render(request, "users/request_blogger.html")


✅ STEP 9 — Admin Approves Requests

Admin → Blogger Request → tick "approved".
Signal fires → BloggerProfile created → user.is_blogger = True.


✅ STEP 10 — Cloudinary Setup

Already installed, but verify:

pip install cloudinary django-cloudinary-storage


Add to settings.py:

INSTALLED_APPS += [
    'cloudinary',
    'cloudinary_storage',
]


And:

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'