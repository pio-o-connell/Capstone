
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

    # Handle new comment submission (allow anonymous comments)
    if request.method == 'POST' and (request.POST.get('action') == 'add_comment' or request.POST.get('content') or request.POST.get('body')):
        # retrieve content from possible field names (content or body)
        content = (request.POST.get('content') or request.POST.get('body') or '').strip()
        if content:
            # author if authenticated, otherwise None
            author = request.user if request.user.is_authenticated else None

            # For anonymous users store a display name if provided, else 'Anonymous'
            name = None
            email = None
            if author:
                name = None
                email = getattr(author, 'email', None)
            else:
                name = request.POST.get('name') or 'Anonymous'
                email = request.POST.get('email') or None

            # IP address (support X-Forwarded-For)
            ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
            if ip and ',' in ip:
                ip = ip.split(',')[0].strip()

            # session id passed from client (populated from localStorage)
            session_id = request.POST.get('anon_session_id') or request.POST.get('session_id') or None

            Comment.objects.create(
                post=post,
                author=author,
                name=name,
                email=email,
                content=content,
                approved=False,
                ip_address=ip,
                session_id=session_id,
            )

        # If we have a session_id for an anonymous user, include it in the redirect
        if not request.user.is_authenticated and session_id:
            return redirect(f"{post.get_absolute_url()}?anon_sess={session_id}")
        return redirect(post.get_absolute_url())

    # Fetch comments: show all approved comments; also show unapproved comments by the current user
    approved_comments = post.comments.filter(approved=True)

    # If the viewer is authenticated, include their unapproved comments (author match).
    # If anonymous but an anon session marker is present in the GET params, include unapproved comments matching that session_id.
    if request.user.is_authenticated:
        user_unapproved = post.comments.filter(approved=False, author=request.user)
    else:
        session_marker = request.GET.get('anon_sess')
        if session_marker:
            user_unapproved = post.comments.filter(approved=False, session_id=session_marker)
        else:
            user_unapproved = Comment.objects.none()

    # Additionally, include unapproved comments that explicitly have the name set to 'Anonymous'
    # (case-insensitive) so these are visible as requested.
    anon_named = post.comments.filter(approved=False, name__iexact='anonymous')

    comments = approved_comments | user_unapproved | anon_named

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
