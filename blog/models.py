from django.db import models
from django.utils.text import slugify, Truncator
from django.urls import reverse
from cloudinary.models import CloudinaryField
from django_summernote.fields import SummernoteTextField
from users.models import CustomUser

class Post(models.Model):
    STATUS_CHOICES = [('draft','Draft'),('published','Published')]
    author = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200)
    content = SummernoteTextField()
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    featured_image = CloudinaryField('image', default='placeholder')
    excerpt = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.title} | written by {self.author}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "post"
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if not self.excerpt and self.content:
            self.excerpt = Truncator(self.content).chars(300)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})



class Comment(models.Model):
    """
    Stores a single comment entry related to CustomUser and Post.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="comments_made",
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    content = SummernoteTextField(null=True, blank=True)  # rich text
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_id = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"
