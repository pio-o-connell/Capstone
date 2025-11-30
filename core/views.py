from django.shortcuts import render

def home(request):
    """
    Homepage view: renders the homepage template.
    """
    return render(request, 'core/home.html')

def contact(request):
    """
    Contact page view.
    """
    return render(request, 'core/contact.html')


def services_home(request):
    """Render the services landing page."""
    return render(request, 'core/services.html')
