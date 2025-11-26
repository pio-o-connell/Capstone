from django.urls import path
from . import views

urlpatterns = [
  path('', views.accounts_home, name='accounts_home'),
  path('login/', views.login_view, name='login'),
  path('register/', views.register_view, name='register'),
  path('logout/', views.logout_view, name='logout'),
]
