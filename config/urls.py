from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from blog.models import Comment, Post
from bookings.models import Booking
from config.admin_site import CustomAdminSite
from users.models import (
    BloggerProfile,
    BloggerRequest,
    CustomUser,
    CustomerProfile,
)

custom_admin = CustomAdminSite(name='custom_admin')

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
    path('users/', include('users.urls')),  # include your users app URLs
    path('summernote/', include('django_summernote.urls')),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    path('bookings/', include('bookings.urls')),
    # Include services namespace so templates can reverse 'services:services_home'
    path(
        'services/',
        include(('services.urls', 'services'), namespace='services'),
    ),

    # Stripe
    # path('checkout/', include('payments.urls')),  # or a view in bookings

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
