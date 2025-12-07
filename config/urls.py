# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('summernote/', include('django_summernote.urls')),
#     path('', include('core.urls')),
#     path('accounts/', include('accounts.urls')),
#     path('blog/', include('blog.urls')),
#     path('bookings/', include('bookings.urls')),
#     # Include services with a namespace so templates can reverse 'services:services_home'
#     path('services/', include(('services.urls', 'services'), namespace='services')),
# ]

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from config.admin_site import CustomAdminSite

custom_admin = CustomAdminSite(name='custom_admin')

# Register your models
from users.models import CustomUser, CustomerProfile, BloggerProfile, BloggerRequest
from blog.models import Post, Comment
from bookings.models import Booking

custom_admin.register(CustomUser)
custom_admin.register(CustomerProfile)
custom_admin.register(BloggerProfile)
custom_admin.register(BloggerRequest)
custom_admin.register(Post)
custom_admin.register(Comment)
custom_admin.register(Booking)








urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/', custom_admin.urls),
    path('summernote/', include('django_summernote.urls')),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    path('bookings/', include('bookings.urls')),
    # Include services with a namespace so templates can reverse 'services:services_home'
    path('services/', include(('services.urls', 'services'), namespace='services')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)