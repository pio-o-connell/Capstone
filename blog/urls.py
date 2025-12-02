from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='blog_home'),
    path('list/', views.post_list, name='post_list'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
    path('<slug:slug>/comment/<int:pk>/edit/', views.comment_edit, name='comment_edit'),
    path('<slug:slug>/comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('create/', views.create_post, name='create_post'),
]

