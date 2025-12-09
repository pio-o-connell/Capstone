from django.urls import path
from . import views
from .views import (
    add_to_cart_ajax,
)

urlpatterns = [
    path('', views.booking_home, name='booking_home'),
    
    path('guest/add/', views.add_to_cart_guest, name='add_to_cart_guest'),
    path('guest/cart/', views.view_cart_guest, name='view_cart_guest'),
    path('guest/confirm/', views.confirm_guest_booking, name='confirm_guest_booking'),

    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/confirm/', views.confirm_cart, name='confirm_cart'),
    path('cart/summary/', views.cart_summary, name='cart_summary'),
    # AJAX
    path('add-to-cart-ajax/', add_to_cart_ajax, name='add_to_cart_ajax'),
]
