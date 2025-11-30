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
