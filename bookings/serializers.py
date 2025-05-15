from rest_framework import serializers
from .models import Hotel, Booking, User, Room  # Added Room import
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from django.core.files.storage import default_storage

class HotelSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.featured_image:
            return request.build_absolute_uri(obj.featured_image.url)
        return None

    class Meta:
        model = Hotel
        fields = [
            'id', 
            'name', 
            'location', 
            'price', 
            'description', 
            'has_pool', 
            'has_gym',
            'image_url',
            
        ]
        read_only_fields = ['id', 'rating']  # Added rating to read-only

class RoomSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    class Meta:
        model = Room
        fields = [
            'id',
            'name',
            'room_type',
            'price',
            'capacity',
            'image_url',
            'hotel',
            'hotel_name',  # For displaying hotel name in frontend
            'is_available'
        ]
        extra_kwargs = {
            'hotel': {'write_only': True}  # Hide in output but needed for creation
        }
class HotelDetailSerializer(serializers.ModelSerializer):
    # this field comes from `related_name='rooms'` on Room.hotel
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model  = Hotel
        fields = [
          'id','name','location','description','has_pool','has_gym',
          'price','is_active','featured_image','rooms'
        ]

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    room_details = RoomSerializer(source='room', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'hotel',
            'room',
            'room_details',  # Nested room info
            'check_in',
            'check_out',
            'status',
            'total_price',
            'created_at'
        ]
        extra_kwargs = {
            'user': {'read_only': True},
            'status': {'read_only': True},
            'total_price': {'read_only': True},
            'created_at': {'read_only': True},
            'hotel': {'required': False}  # Can be inferred from room
        }

    def validate(self, data):
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError({
                'check_out': 'Must be after check-in date'
            })
            
        # Validate room availability
        if 'room' in data and not data['room'].is_available:
            raise serializers.ValidationError({
                'room': 'This room is not available'
            })
            
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'password2',
            'is_admin',
            'phone'  # Added if your model has this
        ]
        extra_kwargs = {
            'username': {
                'validators': [UniqueValidator(queryset=User.objects.all())]
            },
            'is_admin': {'read_only': True},
            'phone': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': 'Password fields must match'
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)