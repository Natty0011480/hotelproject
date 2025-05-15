"""
URL configuration for hotel_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from bookings.views import RoomListAPI
from bookings.views import (
    HotelListAPI,
    CreateBookingAPI,
    RegisterUserAPI,
    HotelFilterAPI  # Make sure this is imported
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', RedirectView.as_view(url='api/hotels/')),
    path('admin/', admin.site.urls),
    
    # API routes
    path('api/hotels/', HotelListAPI.as_view(), name='hotel-list'),
    path('api/hotels/filter/', HotelFilterAPI.as_view(), name='hotel-filter'),
    path('api/bookings/', CreateBookingAPI.as_view(), name='create-booking'),
    path('api/hotels/<int:hotel_id>/rooms/', RoomListAPI.as_view(), name='room-list'),
    # Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration
    path('api/register/', RegisterUserAPI.as_view(), name='register'),
    
    # DRF auth (optional)
    path('api-auth/', include('rest_framework.urls')),
]