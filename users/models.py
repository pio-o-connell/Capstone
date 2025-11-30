# users/models.py
from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class CustomUser(AbstractUser):
    is_customer = models.BooleanField(default=True)
    is_blogger = models.BooleanField(default=False)

    def become_blogger(self):
        self.is_blogger = True
        self.save()
        blogger_group, _ = Group.objects.get_or_create(name='Bloggers')
        blogger_group.user_set.add(self)


class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)


class BloggerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)


class BloggerRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reason = models.TextField()
    approved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
