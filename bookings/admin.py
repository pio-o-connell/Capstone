# bookings/admin.py
from django.contrib import admin
from .models import Booking

# Bookings
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'user', 'date', 'status')
    actions = ['approve_bookings']

    @admin.action(description='Approve selected bookings')
    def approve_bookings(self, request, queryset):
        queryset.update(approved=True)

# Register your models here.
