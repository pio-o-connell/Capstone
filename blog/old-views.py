
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string

from users.models import BloggerRequest
from .models import Post, Comment
from django.db.models import Q
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

            # Determine approval rules for registered users:
            # - If user has at least one previously approved comment, auto-approve this one.
            # - Otherwise (first-time commenter), mark as not approved and notify them.
            approved = False
            if author:
                has_approved_before = Comment.objects.filter(author=author, approved=True).exists()
                if has_approved_before:
                    approved = True
                else:
                    approved = False

            comment = Comment.objects.create(
                post=post,
                author=author,
                name=name,
                email=email,
                content=content,
                approved=approved,
                ip_address=ip,
                session_id=session_id,
            )

            # Inform anonymous posters that their comment is pending approval
            if not author:
                messages.success(request, 'Thanks — your comment was submitted and will be displayed once approved by an administrator.')

            # For registered users who are submitting their first comment (not yet approved)
            if author and not approved:
                messages.success(request, 'Thanks — your comment was submitted and will be displayed once approved by an administrator. Future comments will be approved automatically.')

            # If this is a registered, already-approved commenter and the comment is auto-approved,
            # support AJAX by returning rendered HTML for insertion into the page.
            if author and approved:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('blog/_comment_item.html', {'comment': comment, 'user': request.user, 'post': post}, request=request)
                    return HttpResponse(html, content_type='text/html')

        # If the commenter is anonymous, redirect back to the post and
        # include a fragment so the browser jumps to the messages area.
        if not request.user.is_authenticated and session_id:
            return redirect(f"{post.get_absolute_url()}?anon_sess={session_id}#messages")
        if not request.user.is_authenticated:
            return redirect(f"{post.get_absolute_url()}#messages")
        return redirect(post.get_absolute_url())

    # Fetch comments: include approved comments for everyone, and also include
    # the viewing user's own comments (even if unapproved) so they can see
    # their edits immediately.
    if request.user.is_authenticated:
        comments = post.comments.filter(Q(approved=True) | Q(author=request.user)).order_by('-created_at')
    else:
        comments = post.comments.filter(approved=True).order_by('-created_at')

    context = {
        'post': post,
        'comments': comments,
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

def posts_with_comments(request):
    """List all published posts, each with all comments inline (newest first)."""
    posts = (
        Post.objects.filter(status='published')
        .prefetch_related('comments')
        .order_by('-created_on')
    )
    return render(request, 'blog/posts_with_comments.html', {'posts': posts})


@login_required
def posts_with_pending_comments(request):
    """List only posts that have unapproved comments."""
    posts = (
        Post.objects.filter(status='published', comments__approved=False)
        .prefetch_related('comments')
        .distinct()
        .order_by('-created_on')
    )
    return render(request, 'blog/posts_pending.html', {'posts': posts})