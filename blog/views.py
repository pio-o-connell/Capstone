
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from users.models import BloggerRequest
from .models import Post, Comment
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

    # Handle new comment submission
    if request.method == 'POST' and request.POST.get('action') == 'add_comment':
        if not request.user.is_authenticated:
            return redirect('login')
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(post=post, author=request.user, content=content, approved=False)
        return redirect(post.get_absolute_url())

    # Fetch comments: show all approved comments; also show unapproved comments by the current user
    approved_comments = post.comments.filter(approved=True)
    user_unapproved = post.comments.filter(approved=False, author=request.user) if request.user.is_authenticated else Comment.objects.none()
    comments = approved_comments | user_unapproved

    context = {
        'post': post,
        'comments': comments.order_by('-created_at'),
    }
    return render(request, 'blog/post_detail.html', context)


def comment_edit(request, slug, pk):
    post = get_object_or_404(Post, slug=slug)
    comment = get_object_or_404(Comment, pk=pk, post=post)
    if not request.user.is_authenticated or comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment.content = content
            comment.approved = False  # edits require re-approval
            comment.save()
        return redirect(post.get_absolute_url())

    # For non-POST, redirect back
    return redirect(post.get_absolute_url())


def comment_delete(request, slug, pk):
    post = get_object_or_404(Post, slug=slug)
    comment = get_object_or_404(Comment, pk=pk, post=post)
    if not request.user.is_authenticated or comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        comment.delete()
    return redirect(post.get_absolute_url())

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
