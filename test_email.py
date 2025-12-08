#!/usr/bin/env python
"""
Test email configuration
Run: python test_email.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 50)
print("Testing Email Configuration")
print("=" * 50)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
print(f"EMAIL_HOST_PASSWORD: {'*' * 16 if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'Not set'}")
print("=" * 50)

if settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    try:
        print("\nSending test email...")
        send_mail(
            'Test Email from Django',
            'This is a test email to verify email configuration.',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],  # Send to yourself
            fail_silently=False,
        )
        print("✓ Email sent successfully!")
        print(f"✓ Check inbox: {settings.EMAIL_HOST_USER}")
    except Exception as e:
        print(f"✗ Email failed: {str(e)}")
        print("\nPossible issues:")
        print("1. Check Gmail App Password is correct")
        print("2. Ensure 2-factor authentication is enabled on Gmail")
        print("3. Check firewall/antivirus isn't blocking port 587")
else:
    print("\n⚠ Using console backend - emails will print to console")
    print("Set EMAIL_HOST_USER in env.py to enable SMTP")
