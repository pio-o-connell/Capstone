# bookings/admin.py
from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('service', 'user', 'size', 'quantity', 'date', 'status')
    actions = ['approve_bookings']

    @admin.action(description='Approve selected bookings')
    def approve_bookings(self, request, queryset):
        queryset.update(status='approved')

# Register your models here.
