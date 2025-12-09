from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.accounts_home, name='accounts_home'),  # accounts home
    path('login/', views.login_view, name='login'),       # custom login
    path('logout/', views.logout_view, name='logout'),    # custom logout
    path('register/', views.register_view, name='register'),  # custom register
    path('', include('django.contrib.auth.urls')),       # password reset URLs
]
