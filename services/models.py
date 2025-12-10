from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    small_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
    )
    medium_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
    )
    large_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
    )

    image = models.ImageField(upload_to="services/", blank=True)

    def __str__(self):
        return self.name

    def get_price(self, size):
        size_map = {
            "small": self.small_price,
            "medium": self.medium_price,
            "large": self.large_price,
        }
        return size_map.get(size)
