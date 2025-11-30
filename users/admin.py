from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CustomerProfile, BloggerProfile, BloggerRequest

@admin.action(description='Promote selected users to Bloggers')
def make_bloggers(modeladmin, request, queryset):
    for user in queryset:
        user.become_blogger()

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_customer', 'is_blogger', 'is_staff', 'is_active')
    list_filter = ('is_blogger', 'is_customer', 'is_staff', 'is_active')
    actions = [make_bloggers]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomerProfile)
admin.site.register(BloggerProfile)
admin.site.register(BloggerRequest)
