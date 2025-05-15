from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Hotel, Booking, Room  # Added Room import
from .serializers import HotelSerializer, BookingSerializer, UserRegistrationSerializer, RoomSerializer  # Added RoomSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

User = get_user_model()

class HotelListAPI(generics.ListAPIView):
    serializer_class = HotelSerializer
    queryset = Hotel.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend]  # Add this
    filterset_fields = ['location', 'has_pool'] 
    # Optional: Add pagination
    # pagination_class = PageNumberPagination

class HotelFilterAPI(generics.ListAPIView):
    """
    Separate endpoint for filtered searches
    URL: /api/hotels/filter/?location=Maldives&has_pool=true&min_price=100&max_price=500
    """
    serializer_class = HotelSerializer
    queryset = Hotel.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'has_pool': ['exact'],
        'has_gym': ['exact'],
        'price': ['gte', 'lte']
    }
    search_fields = ['location', 'name']

class RoomListAPI(generics.ListAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]  # Optional: Add if rooms should be protected
    
    def get_queryset(self):
        hotel_id = self.kwargs['hotel_id']
        return Room.objects.filter(
            hotel_id=hotel_id,
            is_available=True
        ).select_related('hotel')  # Optimizes database queries

class CreateBookingAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        booking_data = request.data.copy()
        booking_data['user'] = request.user.id
        
        serializer = BookingSerializer(data=booking_data, context={'request': request})
        if serializer.is_valid():
            # Add room availability check
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
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()