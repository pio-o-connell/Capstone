
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from users.models import BloggerRequest
from .models import Post
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def post_list(request):
    """Render the list of published posts with pagination (6 per page)."""
    post_qs = Post.objects.filter(status='published').order_by('-created_on')
    paginator = Paginator(post_qs, 6)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    posts = page_obj.object_list
    context = {
        'posts': posts,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """Render a single post detail by slug (published posts only)."""
    post = get_object_or_404(Post, slug=slug, status='published')
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def create_post(request):
    if not request.user.is_blogger:
        return redirect('post_list')
        # return HttpResponseForbidden("You are not allowed to create posts.")

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
