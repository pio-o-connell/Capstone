from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required

from .models import Post, Comment


def post_list(request):
    """Public list of published posts."""
    posts = Post.objects.filter(status='published').order_by('-created_on')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    comments = post.comments.filter(approved=True).order_by('-created_at')
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments})


def comment_edit(request, slug, pk):
    # Minimal placeholder: not implemented form handling here
    return HttpResponseNotAllowed(['GET', 'POST'])


def comment_delete(request, slug, pk):
    return HttpResponseNotAllowed(['POST'])


@login_required
def create_post(request):
    return HttpResponseNotAllowed(['GET', 'POST'])


@staff_member_required
def blog_with_comments(request):
    """
    Show all posts with their approved comments inline (most recent comment on top)
    """
    posts = Post.objects.filter(status='published').order_by('-created_on').prefetch_related(
        'comments'
    )

    # Only approved comments are shown
    posts_with_comments = []
    for post in posts:
        approved_comments = post.comments.filter(approved=True).order_by('-created_at')
        posts_with_comments.append((post, approved_comments))

    context = {
        'posts_with_comments': posts_with_comments,
    }
    return render(request, 'blog/blog_with_comments.html', context)


@staff_member_required
def blog_pending_comments(request):
    """
    Show posts that have unapproved comments, displaying only the unapproved comments
    """
    # Fetch posts that have at least one unapproved comment
    posts = Post.objects.filter(comments__approved=False).distinct().order_by('-created_on')

    posts_with_unapproved_comments = []
    for post in posts:
        unapproved_comments = post.comments.filter(approved=False).order_by('-created_at')
        posts_with_unapproved_comments.append((post, unapproved_comments))

    context = {
        'posts_with_unapproved_comments': posts_with_unapproved_comments,
    }
    return render(request, 'blog/blog_pending_comments.html', context)


# Aliases for older URL names (keeps compatibility with urls.py)
posts_with_comments = blog_with_comments
posts_with_pending_comments = blog_pending_comments
