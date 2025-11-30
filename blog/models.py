# from django.db import models
# from users.models import CustomUser

# class Post(models.Model):
#     STATUS_CHOICES = [
#         ('draft', 'Draft'),
#         ('published', 'Published'),
#     ]
#     author = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
#     created_at = models.DateTimeField(auto_now_add=True)

# class Comment(models.Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100, null=True, blank=True)
#     email = models.EmailField(null=True, blank=True)
#     content = models.TextField(null=True, blank=True)
#     approved = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     ip_address = models.GenericIPAddressField(null=True, blank=True)
#     session_id = models.CharField(max_length=40, null=True, blank=True)
from django.db import models
from users.models import CustomUser
from cloudinary.models import CloudinaryField
from django.utils.text import slugify
from django_summernote.fields import SummernoteTextField  # rich text


class Post(models.Model):
    """
    Stores a single blog post entry related to CustomUser.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    author = models.ForeignKey(
        CustomUser, null=True, blank=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=200)
    content = SummernoteTextField()  # rich text
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    featured_image = CloudinaryField('image', default='placeholder')
    excerpt = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Fallback to "post" if title is empty
            base_slug = slugify(self.title) or "post"
            slug = base_slug
            counter = 1

            # Ensure unique slug
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.title} | written by {self.author}"

    def get_absolute_url(self):
        from django.urls import reverse
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
