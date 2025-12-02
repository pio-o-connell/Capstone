from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    path('bookings/', include('bookings.urls')),
    # Include services with a namespace so templates can reverse 'services:services_home'
    path('services/', include(('services.urls', 'services'), namespace='services')),
]

