from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='blog_home'),
    path('list/', views.post_list, name='post_list'),

    #NEW 
    path('with-comments/', views.posts_with_comments, name='posts_with_comments'),
    path('pending-comments/', views.posts_with_pending_comments, name='posts_pending'),

    # Edit a blog post by primary key
    path('edit/<int:pk>/', views.blog_edit, name='blog_edit'),

    path('<slug:slug>/', views.post_detail, name='post_detail'),
    path('<slug:slug>/comment/<int:pk>/edit/', views.comment_edit, name='comment_edit'),
    path('<slug:slug>/comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('create/', views.create_post, name='create_post'),
]

urlpatterns += [
    path('with-comments/', views.blog_with_comments, name='blog_with_comments'),
    path('pending-comments/', views.blog_pending_comments, name='blog_pending_comments'),
]
