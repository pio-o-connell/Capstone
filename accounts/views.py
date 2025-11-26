from django.shortcuts import render

def accounts_home(request):
    return render(request, 'accounts/accounts_home.html')

# Create your views here.

def login_view(request):
    return render(request, 'accounts/login.html')

def register_view(request):
    return render(request, 'accounts/register.html')

def logout_view(request):
    return render(request, 'accounts/logout.html')