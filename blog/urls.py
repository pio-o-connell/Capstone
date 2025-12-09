from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='blog_home'),
    path('start-writing/', views.start_writing, name='start_writing'),
    path('list/', views.post_list, name='post_list'),
    path('dashboard/', views.blogger_dashboard, name='blogger_dashboard'),
    path('with-comments/', views.blog_with_comments, name='blog_with_comments'),
    path(
        'pending-comments/',
        views.blog_pending_comments,
        name='blog_pending_comments',
    ),
    path('post/new/', views.blog_edit, name='blog_create'),
    path('post/<slug:slug>/edit/', views.blog_edit, name='blog_edit'),
    path(
        'post/<slug:slug>/delete/',
        views.blog_delete,
        name='blog_delete',
    ),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
    path(
        '<slug:slug>/comment/<int:pk>/edit/',
        views.comment_edit,
        name='comment_edit',
    ),
    path(
        '<slug:slug>/comment/<int:pk>/delete/',
        views.comment_delete,
        name='comment_delete',
    ),
    path('create/', views.create_post, name='create_post'),
]
