from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from bookings import views
from bookings.views import HotelDetailAPI

from bookings.views import (
    HotelListAPI,
    HotelFilterAPI,
    HotelDetailAPI,
    RoomDetailAPI,
    RoomListByUUIDAPI,        # ← updated name
    RoomBookedRangesAPI,
    CreateBookingAPI,
    RegisterUserAPI,
    StayListAPI,
    StayDetailAPI,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from bookings.auth import EmailTokenObtainPairView

urlpatterns = [
    path('', RedirectView.as_view(url='api/hotels/')),
    path('admin/', admin.site.urls),

    # Hotels
    path('api/hotels/',        HotelListAPI.as_view(),      name='hotel-list'),
    path('api/hotels/filter/', HotelFilterAPI.as_view(),    name='hotel-filter'),
    path('api/hotels/<int:pk>/', HotelDetailAPI.as_view(),  name='hotel-detail'),

    # Rooms
    path(
        'api/hotels/<uuid:hotel_uid>/rooms/',
        RoomListByUUIDAPI.as_view(),
        name='room-list-by-uuid'
    ),

    path('api/rooms/<int:room_id>/booked_ranges/', RoomBookedRangesAPI,          name='room-booked-ranges'),
    path('api/hotels/<uuid:uid>/',     HotelDetailAPI.as_view(), name='hotel-detail-uuid'),
    path('api/hotels/<uuid:uid>/', HotelDetailAPI.as_view(), name='hotel-detail'),


     # List available rooms for a hotel
    path('api/hotels/<uuid:hotel_uid>/rooms/',
         RoomListByUUIDAPI.as_view(), name='room-list'),

    # ▷ NEW: single room detail nested under hotel
    path('api/hotels/<uuid:hotel_uid>/rooms/<uuid:room_uid>/',
         RoomDetailAPI.as_view(), name='room-detail'),

    # Bookings
    path('api/bookings/',      CreateBookingAPI.as_view(),  name='create-booking'),

    # Auth & registration
    path('api/register/',      RegisterUserAPI.as_view(),   name='register'),
    path('api/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
    path('api-auth/',          include('rest_framework.urls')),

    # Stays (all rooms / single room)
    path('api/stays/',         StayListAPI.as_view(),       name='stay-list'),
    path('api/stays/<uuid:uid>/', StayDetailAPI.as_view(), name='stay-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
