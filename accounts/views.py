from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm

# Import email verification functions from users app
from users.views import send_verification_email


def accounts_home(request):
    return render(request, 'accounts/accounts_home.html')


# Login view using Django's AuthenticationForm
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Welcome back! You have successfully logged in.")
            return redirect('home')
    else:
        form = AuthenticationForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email verified
            user.email_verified = False
            user.save()

            print(f"User created: {user.username} ({user.email})")
            print("Sending verification email...")

            # Send verification email
            try:
                send_verification_email(request, user)
                messages.success(
                    request,
                    "Registration successful! Check your email to verify your account.",
                )
                return redirect('home')
            except Exception as e:
                print(f"Email send error: {str(e)}")
                messages.error(
                    request,
                    f"Registration created but email failed to send: {str(e)}",
                )
                return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')
