from django.contrib import admin
from .models import Room, Booking, Review, Hotel, User

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active')
    list_filter = ('location',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available')  # Removed 'room_type'
    list_filter = ('is_available',)  # Removed 'room_type'
    search_fields = ('name', 'description')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'room', 'check_in', 'check_out', 'total_price')
    list_filter = ('check_in', 'check_out')
    search_fields = ('user__username', 'room__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'room__name')
