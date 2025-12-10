# users/models.py
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from cloudinary.models import CloudinaryField
from django_summernote.fields import SummernoteTextField


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
    avatar = CloudinaryField('image', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    approved = models.BooleanField(default=False)  # NEW: admin approval flag
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CustomerProfile for {self.user.username}"


class BloggerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    about = SummernoteTextField(blank=True, null=True)
    avatar = CloudinaryField('image', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"BloggerProfile for {self.user.username}"


class BloggerRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reason = SummernoteTextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Blogger request by {self.user.username}"
