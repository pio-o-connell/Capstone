from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, BloggerRequest

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")


class BloggerRequestForm(forms.ModelForm):
    class Meta:
        model = BloggerRequest
        fields = ["reason"]
