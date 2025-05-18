from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from bookings.views import (
    HotelListAPI, HotelFilterAPI, HotelDetailAPI,
    RoomListAPI, RoomBookedRangesAPI,
    CreateBookingAPI, RegisterUserAPI,
    StayListAPI, StayDetailAPI,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', RedirectView.as_view(url='api/hotels/')),
    path('admin/', admin.site.urls),

    # Hotels
    path('api/hotels/',        HotelListAPI.as_view(),      name='hotel-list'),
    path('api/hotels/filter/', HotelFilterAPI.as_view(),    name='hotel-filter'),
    path('api/hotels/<int:pk>/', HotelDetailAPI.as_view(),  name='hotel-detail'),

    # Rooms
    path('api/hotels/<int:hotel_id>/rooms/',       RoomListAPI.as_view(),        name='room-list'),
    path('api/rooms/<int:room_id>/booked_ranges/', RoomBookedRangesAPI,          name='room-booked-ranges'),

    # Bookings
    path('api/bookings/',      CreateBookingAPI.as_view(),  name='create-booking'),

    # Auth & registration
    path('api/register/',      RegisterUserAPI.as_view(),   name='register'),
    path('api/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
    path('api-auth/',          include('rest_framework.urls')),

    # Stays (all rooms / single room)
    path('api/stays/',         StayListAPI.as_view(),       name='stay-list'),
    path('api/stays/<int:pk>/',StayDetailAPI.as_view(),     name='stay-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
