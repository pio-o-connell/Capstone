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
