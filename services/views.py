# from django.shortcuts import render
# from .models import Service


# def services_home(request):
#     return render(request, 'services/services_home.html')


# def services_view(request):
#     services = Service.objects.all()
#     return render(request, "services/services.html", {"services": services})
from django.shortcuts import render
from .models import Service


def services_home(request):
    """Display the primary services page from the services app."""
    services = Service.objects.all()
    return render(request, "services/services_home.html", {"services": services})
