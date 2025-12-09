from django.shortcuts import render
from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm, BloggerRequestForm
from .models import BloggerRequest

User = get_user_model()


# def register_view(request):
#     # Adjust the template path to where your HTML actually is
#      return render(request, 'registration/registration.html')




# --------------------------
# Register + Email verification
# --------------------------
def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.email_verified = False
            user.save()
            print(f"User created: {user.username} ({user.email})")
            print("Sending verification email...")
            send_verification_email(request, user)
            messages.success(request, "Registration successful! Please check your email to verify your account.")
            return redirect("home")
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def send_verification_email(request, user):
    try:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        verify_url = f"http://{domain}/users/verify/{uid}/{token}/"
        home_url = f"http://{domain}/"
        subject = "Verify your email address"
        message = render_to_string(
            "email/verify_email.html",
            {"user": user, "verify_url": verify_url, "home_url": home_url}
        )
        
        from django.conf import settings
        from_email = settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else "noreply@example.com"
        
        send_mail(
            subject, 
            message, 
            from_email, 
            [user.email], 
            fail_silently=False
        )
        print(f"✓ Verification email sent to {user.email}")
    except Exception as e:
        print(f"✗ Email send failed: {str(e)}")
        raise


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.email_verified = True
        user.save()
        login(request, user)
        messages.success(request, "Your email has been verified! Welcome back.")
        messages.success(request, "You are now logged in.")
        return redirect("home")
    return render(request, "registration/invalid_token.html")


def resend_verification(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            if not user.email_verified:
                send_verification_email(request, user)
        except User.DoesNotExist:
            pass
        messages.info(request, "If the email exists, a verification link was sent.")
        return redirect("resend_verification")
    return render(request, "registration/resend_verification.html")


# --------------------------
# Customer Dashboard
# --------------------------
@login_required
def customer_dashboard(request):
    profile = request.user.customerprofile
    can_request_blogger = profile.approved and not request.user.is_blogger
    return render(request, "dashboard/customer_dashboard.html", {"can_request_blogger": can_request_blogger})


# --------------------------
# Submit Blogger Request
# --------------------------
@login_required
def submit_blogger_request(request):
    profile = request.user.customerprofile
    if not profile.approved:
        messages.error(request, "You must be an approved customer to request blogger access.")
        return redirect("customer_dashboard")

    if request.method == "POST":
        form = BloggerRequestForm(request.POST)
        if form.is_valid():
            BloggerRequest.objects.create(user=request.user, reason=form.cleaned_data["reason"])
            messages.success(request, "Your blogger request has been submitted.")
            return redirect("customer_dashboard")
    else:
        form = BloggerRequestForm()
    return render(request, "dashboard/blogger_request.html", {"form": form})

# Create your views here.
