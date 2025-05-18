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
    HotelListSerializer,
    HotelDetailSerializer,
    RoomSerializer,
    BookingSerializer,
    UserRegistrationSerializer
)

User = get_user_model()


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
    GET /api/hotels/<pk>/
    Retrieve hotel details including nested rooms.
    """
    queryset = Hotel.objects.filter(is_active=True)
    serializer_class = HotelDetailSerializer
    permission_classes = [permissions.AllowAny]


class RoomListAPI(generics.ListAPIView):
    """
    GET /api/hotels/<hotel_id>/rooms/
    List available rooms for a specific hotel.
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
    Returns list of date ranges where room is pending or completed.
    """
    qs = Booking.objects.filter(
        room_id=room_id,
        status__in=[Booking.PENDING, Booking.COMPLETED]
    ).values('check_in', 'check_out')
    return Response(list(qs))


class CreateBookingAPI(APIView):
    """
    POST /api/bookings/
    Create a new booking (status defaults to PENDING).
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
    Register a new user.
    """
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()


# ──────────────────────────────────────────────────────────────────────────────
# Additional "stays" endpoints for all/single room
# ──────────────────────────────────────────────────────────────────────────────


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
    GET /api/stays/<pk>/
    Returns single room details by ID.
    """
    queryset = Room.objects.all().select_related('hotel')
    serializer_class = RoomSerializer
    permission_classes = [permissions.AllowAny]
