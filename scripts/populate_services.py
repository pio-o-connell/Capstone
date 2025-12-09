#!/usr/bin/env python
"""
Populate database with sample services
Run: python scripts/populate_services.py
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Service
from decimal import Decimal

def populate_services():
    """Create sample services."""
    
    print("=" * 60)
    print("Populating Services Database")
    print("=" * 60)
    
    services_data = [
        {
            'name': 'Lawns',
            'description': 'Professional lawn care and maintenance services',
            'small_price': Decimal('20.00'),
            'medium_price': Decimal('30.00'),
            'large_price': Decimal('50.00'),
        },
        {
            'name': 'Hedging',
            'description': 'Expert hedge trimming, cutting, and maintenance',
            'small_price': Decimal('50.00'),
            'medium_price': Decimal('100.00'),
            'large_price': Decimal('150.00'),
        },
        {
            'name': 'Scarifying',
            'description': 'Lawn scarification to remove moss and thatch',
            'small_price': Decimal('100.00'),
            'medium_price': Decimal('100.00'),
            'large_price': Decimal('150.00'),
        },
        {
            'name': 'Shoots & Drains',
            'description': 'Gutter cleaning, downpipe maintenance, and drain services',
            'small_price': Decimal('100.00'),
            'medium_price': Decimal('200.00'),
            'large_price': Decimal('300.00'),
        },
    ]
    
    created_count = 0
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults={
                'description': service_data['description'],
                'small_price': service_data['small_price'],
                'medium_price': service_data['medium_price'],
                'large_price': service_data['large_price'],
            }
        )
        
        if created:
            created_count += 1
            print(f"✓ Created: {service.name}")
            print(f"    Small: €{service.small_price} | Medium: €{service.medium_price} | Large: €{service.large_price}")
        else:
            print(f"⊘ Already exists: {service.name}")
    
    print("=" * 60)
    print(f"✅ Successfully created {created_count} new services!")
    print("=" * 60)
    
    # Print summary
    total_services = Service.objects.count()
    print(f"\nTotal services in database: {total_services}")

if __name__ == '__main__':
    try:
        populate_services()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
