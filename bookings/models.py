from django.db import models
from users.models import CustomUser

class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE, related_name='bookings_cartitems')
    service_name = models.CharField(max_length=200)
    date = models.DateField()
    added_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=200)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
