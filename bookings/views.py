from rest_framework import generics, status, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
import traceback

from .models import Hotel, Booking, Room
from .serializers import (
    HotelListSerializer,
    HotelDetailSerializer,
    RoomSerializer,
    BookingSerializer,
    UserRegistrationSerializer
)

User = get_user_model()

# ───── Hotels ────────────────────────────────────────────────────────────────

class HotelListAPI(generics.ListAPIView):
    """
    GET /api/hotels/
    List all active hotels (no price field in list).
    """
    queryset = Hotel.objects.filter(is_active=True)
    serializer_class = HotelListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['location', 'has_pool']


class HotelFilterAPI(generics.ListAPIView):
    """
    GET /api/hotels/filter/?location=…&has_pool=…&has_gym=…&price__gte=…&price__lte=…
    Advanced hotel search.
    """
    queryset = Hotel.objects.filter(is_active=True)
    serializer_class = HotelListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'has_pool': ['exact'],
        'has_gym': ['exact'],
        'price': ['gte', 'lte'],
    }
    search_fields = ['location', 'name']


class HotelDetailAPI(generics.RetrieveAPIView):
    """
    GET /api/hotels/<uuid:uid>/
    Retrieve hotel details including nested rooms.
    """
    queryset = Hotel.objects.filter(is_active=True)
    serializer_class = HotelDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'uid'


# ───── Rooms ─────────────────────────────────────────────────────────────────

class RoomListByUUIDAPI(generics.ListAPIView):
    """
    GET /api/hotels/<uuid:hotel_uid>/rooms/
    List all rooms for the hotel matching that UUID (public).
    """
    serializer_class = RoomSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        hotel_uid = self.kwargs.get('hotel_uid')
        return Room.objects.filter(hotel__uid=hotel_uid)


class RoomDetailAPI(generics.RetrieveAPIView):
    """
    GET /api/hotels/<uuid:hotel_uid>/rooms/<uuid:room_uid>/
    Retrieve one room by UID under a given hotel.
    """
    serializer_class = RoomSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'uid'
    lookup_url_kwarg = 'room_uid'

    def get_queryset(self):
        hotel_uid = self.kwargs['hotel_uid']
        return Room.objects.filter(hotel__uid=hotel_uid)


@api_view(['GET'])
def RoomBookedRangesAPI(request, room_id):
    """
    GET /api/rooms/<room_id>/booked_ranges/
    Returns date ranges of past or pending bookings for a room.
    """
    qs = Booking.objects.filter(
        room_id=room_id,
        status__in=[Booking.PENDING, Booking.COMPLETED]
    ).values('check_in', 'check_out')
    return Response(list(qs))


# ───── Booking ───────────────────────────────────────────────────────────────

class CreateBookingAPI(APIView):
    """
    POST /api/bookings/
    Create a new booking; requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                booking = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                traceback.print_exc()  # for terminal debugging
                return Response(
                    {"detail": "A booking already exists for this room and date range."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ───── User Registration ─────────────────────────────────────────────────────

class RegisterUserAPI(generics.CreateAPIView):
    """
    POST /api/register/
    Register a new user.
    """
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()


# ───── Stays (all rooms) ─────────────────────────────────────────────────────

class StayListAPI(generics.ListAPIView):
    """
    GET /api/stays/
    Returns all rooms regardless of availability.
    """
    queryset = Room.objects.all().select_related('hotel')
    serializer_class = RoomSerializer
    permission_classes = [permissions.AllowAny]


class StayDetailAPI(generics.RetrieveAPIView):
    """
    GET /api/stays/<uuid:uid>/
    Returns single room details by its UUID.
    """
    queryset = Room.objects.all().select_related('hotel')
    serializer_class = RoomSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'uid'
    lookup_url_kwarg = 'uid'
