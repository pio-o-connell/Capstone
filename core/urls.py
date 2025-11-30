from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),           # Homepage
    path('contact/', views.contact, name='contact'),  # Contact page
    path('services/', views.services_home, name='services_home'),
]
