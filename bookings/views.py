from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Hotel, Booking, Room
from .serializers import (
    HotelSerializer,
    HotelDetailSerializer,
    BookingSerializer,
    RoomSerializer,
    UserRegistrationSerializer
)

User = get_user_model()


class HotelListAPI(generics.ListAPIView):
    serializer_class = HotelSerializer
    queryset = Hotel.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['location', 'has_pool']


class HotelFilterAPI(generics.ListAPIView):
    """
    GET /api/hotels/filter/?location=…&has_pool=…&has_gym=…&price__gte=…&price__lte=…
    """
    serializer_class = HotelSerializer
    queryset = Hotel.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'has_pool': ['exact'],
        'has_gym': ['exact'],
        'price': ['gte', 'lte'],
    }
    search_fields = ['location', 'name']


class HotelDetailAPI(generics.RetrieveAPIView):
    """
    GET /api/hotels/<pk>/
    Returns one hotel + its `rooms` array.
    """
    queryset = Hotel.objects.filter(is_active=True)
    serializer_class = HotelDetailSerializer
    permission_classes = [permissions.AllowAny]


class RoomListAPI(generics.ListAPIView):
    """
    GET /api/hotels/<hotel_id>/rooms/
    Returns all available rooms for that hotel.
    """
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        hotel_id = self.kwargs['hotel_id']
        return Room.objects.filter(
            hotel_id=hotel_id,
            is_available=True
        ).select_related('hotel')


@api_view(['GET'])
def RoomBookedRangesAPI(request, room_id):
    """
    GET /api/rooms/<room_id>/booked_ranges/
    Returns list of {"check_in","check_out"} for PENDING & COMPLETED bookings.
    """
    qs = Booking.objects.filter(
        room_id=room_id,
        status__in=[Booking.PENDING, Booking.COMPLETED]
    ).values('check_in', 'check_out')
    return Response(list(qs))


class CreateBookingAPI(APIView):
    """
    POST /api/bookings/
    Creates a new booking (status defaults to PENDING).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = BookingSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            room = serializer.validated_data['room']
            if not room.is_available:
                return Response(
                    {"error": "This room is not available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserAPI(generics.CreateAPIView):
    """
    POST /api/register/
    Registers a new user.
    """
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()


# ──────────────────────────────────────────────────────────────────────────────
# New “stays” endpoints:
# ──────────────────────────────────────────────────────────────────────────────

class StayListAPI(generics.ListAPIView):
    """
    GET /api/stays/
    Returns ALL rooms (regardless of availability).
    """
    queryset = Room.objects.all().select_related('hotel')
    serializer_class = RoomSerializer
    permission_classes = [permissions.AllowAny]


class StayDetailAPI(generics.RetrieveAPIView):
    """
    GET /api/stays/<pk>/
    Returns one room’s details by ID.
    """
    queryset = Room.objects.all().select_related('hotel')
    serializer_class = RoomSerializer
    permission_classes = [permissions.AllowAny]
