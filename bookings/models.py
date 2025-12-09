# from django.db import models
# from users.models import CustomUser

# class CartItem(models.Model):
#     user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE, related_name='bookings_cartitems')
#     service_name = models.CharField(max_length=200)
#     date = models.DateField()
#     added_at = models.DateTimeField(auto_now_add=True)
#     session_id = models.CharField(max_length=40, null=True, blank=True)

# class Booking(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#         ('cancelled', 'Cancelled'),
#     ]
#     user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
#     service_name = models.CharField(max_length=200)
#     date = models.DateField()
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)
from django.db import models
from users.models import CustomUser
from services.models import Service  # import from services app


class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE, related_name='cart_items')
    session_id = models.CharField(max_length=40, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE,default=1)
    size = models.CharField(max_length=10, choices=[("small","Small"),("medium","Medium"),("large","Large")], default="small")
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.service.get_price(self.size)

    def __str__(self):
        return f"{self.service.name} ({self.size}) x{self.quantity}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('approved','Approved'),
        ('rejected','Rejected'),
        ('cancelled','Cancelled'),
    ]
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    size = models.CharField(max_length=10, choices=[("small","Small"),("medium","Medium"),("large","Large")], default="small")
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.service.get_price(self.size)

    def __str__(self):
        return f"Booking: {self.service.name} ({self.size}) x{self.quantity} - {self.status}"
