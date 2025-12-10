from django import forms
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
                else:
                    comment.approved = False

                if anon_session and hasattr(comment, 'anon_session_id'):
                    setattr(comment, 'anon_session_id', anon_session)

                comment.save()

                is_xhr = (
                    request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
                )
                if is_xhr:
                    return render(
                        request,
                        'blog/_comment_item.html',
                        {
                            'comment': comment,
                            'post': post,
                            'user': request.user,
                        },
                    )

                return redirect(post.get_absolute_url() + '#comments')

    comments = post.comments.filter(approved=True).order_by('-created_at')
    return render(
        request,
        'blog/post_detail.html',
        {
            'post': post,
            'comments': comments,
        },
    )


def comment_edit(request, slug, pk):
    post = get_object_or_404(
        Post,
        slug=slug,
        status='published',
    )
    comment = get_object_or_404(Comment, pk=pk, post=post)
    user = request.user
    if not (
        user.is_authenticated
        and (comment.author == user or user.is_staff)
    ):
        return HttpResponseForbidden(
            'You do not have permission to edit this comment.',
        )

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment.content = content
            if not user.is_staff:
                comment.approved = False
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

    user = request.user
    if not (
        user.is_authenticated
        and (comment.author == user or user.is_staff)
    ):
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
