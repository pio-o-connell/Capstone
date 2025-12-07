# from django.contrib.admin.views.decorators import staff_member_required
# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import HttpResponseNotAllowed, HttpResponseForbidden
# from django.contrib.auth.decorators import login_required

# from .models import Post, Comment


# def post_list(request):
#     """Public list of published posts."""
#     posts = Post.objects.filter(status='published').order_by('-created_on')
#     return render(request, 'blog/post_list.html', {'posts': posts})


# def post_detail(request, slug):
#     post = get_object_or_404(Post, slug=slug, status='published')

#     # Handle new comment submissions via POST
#     if request.method == 'POST':
#         action = request.POST.get('action', 'add_comment')
#         # Create a new comment (minimal validation)
#         if action == 'add_comment':
#             content = request.POST.get('content', '').strip()
#             name = request.POST.get('name', '').strip() or None
#             email = request.POST.get('email', '').strip() or None
#             anon_session = request.POST.get('anon_session_id') or None

#             if content:
#                 comment = Comment(
#                     post=post,
#                     content=content,
#                     name=name,
#                     email=email,
#                 )
#                 # Associate an authenticated user as the author
#                 if request.user.is_authenticated:
#                     comment.author = request.user
#                     # Auto-approve comments from authenticated users
#                     comment.approved = True
#                 else:
#                     comment.approved = False

#                 # Optionally store anon_session if the model supports it
#                 try:
#                     if anon_session and hasattr(comment, 'anon_session_id'):
#                         setattr(comment, 'anon_session_id', anon_session)
#                 except Exception:
#                     pass

#                 comment.save()

#                 # If this is an AJAX (XHR) request, return the rendered comment fragment
#                 is_xhr = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
#                 if is_xhr:
#                     # Render the single comment partial and return HTML
#                     return render(request, 'blog/_comment_item.html', {'comment': comment, 'post': post, 'user': request.user})

#                 # Fallback: redirect back to the post detail (anchor to comments)
#                 return redirect(post.get_absolute_url() + '#comments')

#         # For other actions, fall through to rendering the page

#     comments = post.comments.filter(approved=True).order_by('-created_at')
#     return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments})


# def comment_edit(request, slug, pk):
#     post = get_object_or_404(Post, slug=slug, status='published')
#     comment = get_object_or_404(Comment, pk=pk, post=post)

#     # Only the comment author or staff may edit
#     user = request.user
#     if not (user.is_authenticated and (comment.author == user or user.is_staff)):
#         return HttpResponseForbidden('You do not have permission to edit this comment.')

#     if request.method == 'POST':
#         # Update the comment content
#         content = request.POST.get('content', '').strip()
#         if content:
#             comment.content = content
#             # After edit, mark as unapproved unless edited by staff
#             if not user.is_staff:
#                 comment.approved = False
#             comment.save()

#         # Redirect back to the post (anchor to the comment)
#         try:
#             return redirect(post.get_absolute_url() + '#comment-' + str(comment.pk))
#         except Exception:
#             return redirect(post.get_absolute_url())

#     # For non-POST (GET), render a minimal edit form fragment (optional)
#     return render(request, 'blog/comment_edit_form.html', {'post': post, 'comment': comment})


# def comment_delete(request, slug, pk):
#     post = get_object_or_404(Post, slug=slug, status='published')
#     comment = get_object_or_404(Comment, pk=pk, post=post)

#     if request.method != 'POST':
#         return HttpResponseNotAllowed(['POST'])

#     user = request.user
#     if not (user.is_authenticated and (comment.author == user or user.is_staff)):
#         return HttpResponseForbidden('You do not have permission to delete this comment.')

#     # perform deletion
#     comment.delete()

#     # If AJAX, return a small JSON response; otherwise redirect back to the post
#     is_xhr = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
#     if is_xhr:
#         from django.http import JsonResponse
#         return JsonResponse({'deleted': True})

#     return redirect(post.get_absolute_url())


# @login_required
# def create_post(request):
#     return HttpResponseNotAllowed(['GET', 'POST'])


# @staff_member_required
# def blog_with_comments(request):
#     """
#     Show all posts with their approved comments inline (most recent comment on top)
#     """
#     posts = Post.objects.filter(status='published').order_by('-created_on').prefetch_related(
#         'comments'
#     )

#     # Only approved comments are shown
#     posts_with_comments = []
#     for post in posts:
#         approved_comments = post.comments.filter(approved=True).order_by('-created_at')
#         posts_with_comments.append((post, approved_comments))

#     context = {
#         'posts_with_comments': posts_with_comments,
#     }
#     return render(request, 'blog/blog_with_comments.html', context)


# @staff_member_required
# def blog_pending_comments(request):
#     """
#     Show posts that have unapproved comments, displaying only the unapproved comments
#     """
#     # Fetch posts that have at least one unapproved comment
#     posts = Post.objects.filter(comments__approved=False).distinct().order_by('-created_on')

#     posts_with_unapproved_comments = []
#     for post in posts:
#         unapproved_comments = post.comments.filter(approved=False).order_by('-created_at')
#         posts_with_unapproved_comments.append((post, unapproved_comments))

#     context = {
#         'posts_with_unapproved_comments': posts_with_unapproved_comments,
#     }
#     return render(request, 'blog/blog_pending_comments.html', context)


# # Aliases for older URL names (keeps compatibility with urls.py)
# posts_with_comments = blog_with_comments
# posts_with_pending_comments = blog_pending_comments
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Post, Comment


def post_list(request):
    """Public list of published posts with pagination (6 per page)."""
    posts = Post.objects.filter(status='published').order_by('-created_on')

    # Sort so logged-in user's posts appear first
    if request.user.is_authenticated:
        user_posts = [p for p in posts if p.author == request.user]
        other_posts = [p for p in posts if p.author != request.user]
        posts = user_posts + other_posts

    # Mark posts that belong to the logged-in user
    for post in posts:
        post.is_mine = request.user.is_authenticated and post.author == request.user

    # Paginate with 6 posts per page
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/post_list.html', {'page_obj': page_obj, 'is_paginated': page_obj.has_other_pages(), 'posts': page_obj})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')

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

                is_xhr = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
                if is_xhr:
                    return render(request, 'blog/_comment_item.html', {'comment': comment, 'post': post, 'user': request.user})

                return redirect(post.get_absolute_url() + '#comments')

    comments = post.comments.filter(approved=True).order_by('-created_at')
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments})


def comment_edit(request, slug, pk):
    post = get_object_or_404(Post, slug=slug, status='published')
    comment = get_object_or_404(Comment, pk=pk, post=post)
    user = request.user
    if not (user.is_authenticated and (comment.author == user or user.is_staff)):
        return HttpResponseForbidden('You do not have permission to edit this comment.')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment.content = content
            if not user.is_staff:
                comment.approved = False
            comment.save()
        try:
            return redirect(post.get_absolute_url() + '#comment-' + str(comment.pk))
        except Exception:
            return redirect(post.get_absolute_url())

    return render(request, 'blog/comment_edit_form.html', {'post': post, 'comment': comment})


def comment_delete(request, slug, pk):
    post = get_object_or_404(Post, slug=slug, status='published')
    comment = get_object_or_404(Comment, pk=pk, post=post)
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    user = request.user
    if not (user.is_authenticated and (comment.author == user or user.is_staff)):
        return HttpResponseForbidden('You do not have permission to delete this comment.')

    comment.delete()

    is_xhr = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_xhr:
        from django.http import JsonResponse
        return JsonResponse({'deleted': True})

    return redirect(post.get_absolute_url())


@login_required
def create_post(request):
    return HttpResponseNotAllowed(['GET', 'POST'])


@login_required
def blog_edit(request, pk):
    """Simple edit view for a Post. Only author or staff can edit."""
    post = get_object_or_404(Post, pk=pk)

    user = request.user
    if not (user.is_staff or post.author == user):
        return HttpResponseForbidden('You do not have permission to edit this post.')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        excerpt = request.POST.get('excerpt', '').strip()
        status = request.POST.get('status', post.status)

        if title:
            post.title = title
        if content:
            post.content = content
        post.excerpt = excerpt
        post.status = status
        post.save()

        return redirect(post.get_absolute_url())

    # GET -> render a simple edit form
    return render(request, 'blog/post_edit_form.html', {'post': post})


@staff_member_required
def blog_with_comments(request):
    posts = Post.objects.filter(status='published').order_by('-created_on').prefetch_related('comments')
    posts_with_comments = [(post, post.comments.filter(approved=True).order_by('-created_at')) for post in posts]

    return render(request, 'blog/blog_with_comments.html', {'posts_with_comments': posts_with_comments})


@staff_member_required
def blog_pending_comments(request):
    posts = Post.objects.filter(comments__approved=False).distinct().order_by('-created_on')
    posts_with_unapproved_comments = [(post, post.comments.filter(approved=False).order_by('-created_at')) for post in posts]

    return render(request, 'blog/blog_pending_comments.html', {'posts_with_unapproved_comments': posts_with_unapproved_comments})


# Aliases for older URL names
posts_with_comments = blog_with_comments
posts_with_pending_comments = blog_pending_comments
