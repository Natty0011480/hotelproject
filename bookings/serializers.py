from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Hotel, Room, Booking, User

# Serializers for Hotel
class HotelListSerializer(serializers.ModelSerializer):
    uid = serializers.UUIDField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = ['uid', 'name', 'location', 'stars', 'amenities', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image_url:
            return obj.image_url
        if obj.featured_image:
            return request.build_absolute_uri(obj.featured_image.url)
        return None

class HotelDetailSerializer(serializers.ModelSerializer):
    uid = serializers.UUIDField(read_only=True)
    image_url = serializers.SerializerMethodField()
    rooms = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = [
            'uid', 'name', 'location', 'description',
            'price', 'stars', 'amenities', 'image_url', 'rooms'
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image_url:
            return obj.image_url
        if obj.featured_image:
            return request.build_absolute_uri(obj.featured_image.url)
        return None

    def get_rooms(self, obj):
        # Use RoomSerializer defined below
        rooms_qs = obj.rooms.filter(is_available=True)
        return RoomSerializer(rooms_qs, many=True, context=self.context).data

# Serializer for Room
class RoomSerializer(serializers.ModelSerializer):
    uid = serializers.UUIDField(read_only=True)
    hotel = serializers.UUIDField(source='hotel.uid', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'uid', 'hotel', 'name', 'description',
            'bed_count', 'bathroom_count', 'bed_type',
            'price', 'capacity', 'is_available', 'image_url'
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

# Serializer for Booking
class BookingSerializer(serializers.ModelSerializer):
    uid = serializers.UUIDField(read_only=True)
    room_details = RoomSerializer(source='room', read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    hotel = serializers.SlugRelatedField(
        queryset=Hotel.objects.all(),
        slug_field='uid'
    )
    room = serializers.SlugRelatedField(
        queryset=Room.objects.all(),
        slug_field='uid'
    )

    class Meta:
        model = Booking
        fields = [
            'uid', 'user', 'hotel', 'room', 'room_details',
            'check_in', 'check_out', 'status', 'total_price', 'created_at'
        ]
        read_only_fields = ['uid', 'status', 'user', 'created_at']

    def validate(self, data):
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        room = data.get('room')

        if check_in and check_out:
            if check_in >= check_out:
                raise serializers.ValidationError({'check_out': 'Check-out must be after check-in.'})

            if check_in < timezone.now().date():
                raise serializers.ValidationError({'check_in': 'Check-in cannot be in the past.'})

        if room:
            # Check overlapping bookings
            overlapping = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
                status__in=[Booking.PENDING, Booking.COMPLETED]
            )
            if overlapping.exists():
                raise serializers.ValidationError("This room is already booked for the selected dates.")

            # Check availability
            if not room.is_available:
                raise serializers.ValidationError({'room': 'This room is not currently available.'})

        return data

    def create(self, validated_data):
        # Automatically assign the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

# Serializer for User registration
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2', 'is_admin', 'phone']
        extra_kwargs = {
            'is_admin': {'read_only': True},
            'phone': {'required': False}
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({'password': 'Passwords must match'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        return User.objects.create_user(**validated_data)
