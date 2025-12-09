#!/usr/bin/env python
"""
Populate database with sample bookings for existing customers
Run: python scripts/populate_bookings.py
"""
import os
import sys
import django
from pathlib import Path
from datetime import date, timedelta
import random

# Setup Django
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser
from services.models import Service
from bookings.models import Booking

def populate_bookings():
    """Create sample bookings for existing users."""
    
    print("=" * 60)
    print("Populating Bookings Database")
    print("=" * 60)
    
    # Get all users
    users = CustomUser.objects.filter(is_superuser=False)
    if not users.exists():
        print("❌ No regular users found. Please create users first.")
        return
    
    print(f"✓ Found {users.count()} users")
    
    # Get all services
    services = Service.objects.all()
    if not services.exists():
        print("❌ No services found. Please create services first.")
        return
    
    print(f"✓ Found {services.count()} services")
    
    # Define booking scenarios
    sizes = ['small', 'medium', 'large']
    statuses = ['pending', 'approved', 'rejected', 'cancelled']
    status_weights = [0.4, 0.4, 0.1, 0.1]  # More pending and approved
    
    # Generate bookings
    created_count = 0
    
    for user in users:
        # Each user gets 2-5 random bookings
        num_bookings = random.randint(2, 5)
        
        for i in range(num_bookings):
            service = random.choice(services)
            size = random.choice(sizes)
            quantity = random.randint(1, 3)
            
            # Random date in the next 60 days
            days_ahead = random.randint(1, 60)
            booking_date = date.today() + timedelta(days=days_ahead)
            
            # Status (more pending/approved than rejected/cancelled)
            status = random.choices(statuses, weights=status_weights)[0]
            
            # Create booking
            booking = Booking.objects.create(
                user=user,
                service=service,
                size=size,
                quantity=quantity,
                date=booking_date,
                status=status
            )
            
            created_count += 1
            print(f"✓ Created: {user.username} - {service.name} ({size}) x{quantity} - {status} on {booking_date}")
    
    print("=" * 60)
    print(f"✅ Successfully created {created_count} bookings!")
    print("=" * 60)
    
    # Print summary by status
    print("\nBooking Summary:")
    for status_choice in statuses:
        count = Booking.objects.filter(status=status_choice).count()
        print(f"  {status_choice.capitalize()}: {count}")

if __name__ == '__main__':
    try:
        populate_bookings()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
