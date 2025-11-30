from django.db import models
from django.conf import settings

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=200)  # store the service name
    date = models.DateTimeField()  # the service date selected by user
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.service_name} for {self.user}"


