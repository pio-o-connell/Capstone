from django import forms
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.text import Truncator

from .models import Post, Comment
from .forms import PostForm
from users.models import BloggerRequest

SITE_SESSION_COOKIE = 'site_session_id'
SITE_SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 year

def _queue_blogger_request(user, post):
    if not user or not user.is_authenticated:
        return
    if getattr(user, 'is_blogger', False):
        return

    reason = Truncator(post.content or '').chars(300)
    BloggerRequest.objects.get_or_create(
        user=user,
        post=post,
        defaults={'reason': reason},
    )


def _lock_post_form_status(post_form):
    if 'status' in post_form.fields:
        status_field = post_form.fields['status']
        status_field.initial = 'draft'
        status_field.required = False
        status_field.widget = forms.HiddenInput()


def _ensure_session_key(request):
    """Guarantee the request has a usable session key and return it."""
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key
    return session_key


def _get_site_session_cookie(request):
    return request.COOKIES.get(SITE_SESSION_COOKIE)


def _set_site_session_cookie(response, session_token):
    if not session_token:
        return response
    response.set_cookie(
        SITE_SESSION_COOKIE,
        session_token,
        max_age=SITE_SESSION_COOKIE_MAX_AGE,
        samesite='Lax',
        secure=getattr(settings, 'SESSION_COOKIE_SECURE', False),
    )
    return response


def _guest_session_tokens(request):
    tokens = []
    cookie_token = _get_site_session_cookie(request)
    if cookie_token:
        tokens.append(cookie_token)

    session_key = request.session.session_key
    if not session_key:
        session_key = _ensure_session_key(request)
    if session_key:
        tokens.append(session_key)

    if request.method == 'POST':
        anon_field = request.POST.get('anon_session_id')
    else:
        anon_field = request.GET.get('anon_session_id')
    if anon_field:
        tokens.append(anon_field)

    return [token for token in tokens if token]


def _can_manage_comment(request, comment):
    """
    Determine whether the current request is allowed to edit/delete the comment.
    Authenticated users can manage their own comments (or any comment if staff).
    Guests can manage comments tied to their session key.
    """
    if request.user.is_authenticated:
        return request.user.is_staff or comment.author == request.user

    if not comment.session_id:
        return False

    session_tokens = _guest_session_tokens(request)
    return any(comment.session_id == token for token in session_tokens)


def post_list(request):
    """Public list of published posts with pagination (6 per page)."""
    posts = (
        Post.objects.filter(status='published')
        .order_by('-created_on')
    )

    # Sort so logged-in user's posts appear first
    if request.user.is_authenticated:
        user_posts = [p for p in posts if p.author == request.user]
        other_posts = [p for p in posts if p.author != request.user]
        posts = user_posts + other_posts

    # Mark posts that belong to the logged-in user
    for post in posts:
        post.is_mine = (
            request.user.is_authenticated and post.author == request.user
        )

    # Paginate with 6 posts per page
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    is_blogger = (
        request.user.is_authenticated
        and hasattr(request.user, 'bloggerprofile')
    )

    return render(
        request,
        'blog/post_list.html',
        {
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'posts': page_obj,
            'is_blogger': is_blogger,
        },
    )


def start_writing(request):
    is_blogger = (
        request.user.is_authenticated
        and hasattr(request.user, 'bloggerprofile')
    )
    if is_blogger:
        return redirect('blogger_dashboard')

    if not request.user.is_authenticated:
        messages.info(
            request,
            'Please create a customer account before submitting a draft.',
        )
        return redirect('register')

    if request.method == 'POST':
        form_data = request.POST.copy()
        form_data.setdefault('status', 'draft')
        form = PostForm(form_data, request.FILES)
        _lock_post_form_status(form)
        if form.is_valid():
            new_post = form.save(commit=False)
            if request.user.is_authenticated:
                new_post.author = request.user
            new_post.status = 'draft'
            new_post.save()
            _queue_blogger_request(request.user, new_post)
            return render(
                request,
                'blog/blog_submission_confirmation.html',
                {
                    'post': new_post,
                    'is_guest_submission': not request.user.is_authenticated,
                },
            )
    else:
        form = PostForm()
        _lock_post_form_status(form)

    return render(
        request,
        'blog/blog_start_writing.html',
        {
            'form': form,
            'requires_login': not request.user.is_authenticated,
        },
    )


def post_detail(request, slug):
    post = get_object_or_404(
        Post,
        slug=slug,
        status='published',
    )

    session_key = request.session.session_key
    if not session_key:
        session_key = _ensure_session_key(request)

    site_session_cookie = _get_site_session_cookie(request)
    guest_session_id = None
    if not request.user.is_authenticated:
        guest_session_id = site_session_cookie or session_key

    if request.method == 'POST':
        action = request.POST.get('action', 'add_comment')
        if action == 'add_comment':
            content = request.POST.get('content', '').strip()
            name = request.POST.get('name', '').strip() or None
            email = request.POST.get('email', '').strip() or None
            anon_session = request.POST.get('anon_session_id') or None

            if content:
                comment = Comment(
                    post=post,
                    content=content,
                    name=name,
                    email=email,
                )
                if request.user.is_authenticated:
                    comment.author = request.user
                comment.approved = True

                if request.user.is_authenticated:
                    session_identifier = session_key
                else:
                    session_identifier = (
                        anon_session
                        or site_session_cookie
                        or session_key
                    )
                if session_identifier and hasattr(comment, 'session_id'):
                    comment.session_id = session_identifier

                comment.save()

                is_xhr = (
                    request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
                )
                if not request.user.is_authenticated:
                    guest_session_id = session_identifier or guest_session_id

                if is_xhr:
                    response = render(
                        request,
                        'blog/_comment_item.html',
                        {
                            'comment': comment,
                            'post': post,
                            'user': request.user,
                            'guest_session_id': guest_session_id,
                        },
                    )
                else:
                    response = redirect(post.get_absolute_url() + '#comments')

                if not request.user.is_authenticated:
                    response = _set_site_session_cookie(response, guest_session_id)
                return response

    comments = post.comments.filter(approved=True).order_by('-created_at')
    response = render(
        request,
        'blog/post_detail.html',
        {
            'post': post,
            'comments': comments,
            'guest_session_id': guest_session_id,
        },
    )
    if not request.user.is_authenticated:
        response = _set_site_session_cookie(
            response,
            guest_session_id or site_session_cookie or session_key,
        )
    return response


def comment_edit(request, slug, pk):
    post = get_object_or_404(
        Post,
        slug=slug,
        status='published',
    )
    comment = get_object_or_404(Comment, pk=pk, post=post)
    if not _can_manage_comment(request, comment):
        return HttpResponseForbidden(
            'You do not have permission to edit this comment.',
        )

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment.content = content
            comment.save()
        try:
            anchor = f"{post.get_absolute_url()}#comment-{comment.pk}"
            return redirect(anchor)
        except Exception:
            return redirect(post.get_absolute_url())

    return render(
        request,
        'blog/comment_edit_form.html',
        {
            'post': post,
            'comment': comment,
        },
    )


def comment_delete(request, slug, pk):
    post = get_object_or_404(
        Post,
        slug=slug,
        status='published',
    )
    comment = get_object_or_404(Comment, pk=pk, post=post)
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    if not _can_manage_comment(request, comment):
        return HttpResponseForbidden(
            'You do not have permission to delete this comment.',
        )

    comment.delete()

    is_xhr = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_xhr:
        from django.http import JsonResponse
        return JsonResponse({'deleted': True})

    return redirect(post.get_absolute_url())


@login_required
def create_post(request):
    return HttpResponseNotAllowed(['GET', 'POST'])


@staff_member_required
def blog_with_comments(request):
    posts = (
        Post.objects.filter(status='published')
        .order_by('-created_on')
        .prefetch_related('comments')
    )
    posts_with_comments = [
        (post, post.comments.filter(approved=True).order_by('-created_at'))
        for post in posts
    ]

    return render(
        request,
        'blog/blog_with_comments.html',
        {
            'posts_with_comments': posts_with_comments,
        },
    )


@staff_member_required
def blog_pending_comments(request):
    posts = (
        Post.objects.filter(comments__approved=False)
        .distinct()
        .order_by('-created_on')
    )
    posts_with_unapproved_comments = [
        (post, post.comments.filter(approved=False).order_by('-created_at'))
        for post in posts
    ]

    return render(
        request,
        'blog/blog_pending_comments.html',
        {
            'posts_with_unapproved_comments': posts_with_unapproved_comments,
        },
    )


# Aliases for older URL names
posts_with_comments = blog_with_comments
posts_with_pending_comments = blog_pending_comments


@login_required
def blogger_dashboard(request):
    posts = Post.objects.filter(author=request.user)
    return render(
        request,
        "blog/blogger_dashboard.html",
        {"posts": posts},
    )


@login_required
def blog_edit(request, slug=None):
    if slug:
        post = get_object_or_404(Post, slug=slug)
        if post.author != request.user and not request.user.is_superuser:
            return HttpResponseForbidden()
    else:
        post = None

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            new_post = form.save(commit=False)
            if not post:
                new_post.author = request.user
            new_post.save()
            if not post:
                _queue_blogger_request(request.user, new_post)
            action = 'updated' if post else 'created'
            messages.success(request, f"Post {action} successfully.")
            return redirect("blogger_dashboard")
    else:
        form = PostForm(instance=post)

    return render(
        request,
        "blog/blog_edit.html",
        {
            "form": form,
            "post": post,
        },
    )


def blog_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user and not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect("blogger_dashboard")

    return render(
        request,
        "blog/blog_delete_confirm.html",
        {"post": post},
    )
