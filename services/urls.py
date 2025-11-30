from django.urls import path
from . import views

# Allow reversing as 'services:services_home' when the include uses a namespace
app_name = 'services'

urlpatterns = [
    path('', views.services_home, name='services_home'),
]
