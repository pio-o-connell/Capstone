# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('submit-blogger-request/', views.submit_blogger_request, name='submit_blogger_request'),
]
