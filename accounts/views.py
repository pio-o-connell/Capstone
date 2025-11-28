from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm


def accounts_home(request):
    return render(request, 'accounts/accounts_home.html')


# Login view using Django's AuthenticationForm
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    return render(request, 'accounts/register.html')


def logout_view(request):
    logout(request)
    return redirect('home')