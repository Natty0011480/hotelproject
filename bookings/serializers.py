from rest_framework import serializers
from .models import Hotel, Room, Booking, User

class HotelListSerializer(serializers.ModelSerializer):
    uid       = serializers.UUIDField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = Hotel
        fields = ['uid','name','location','stars','amenities','image_url']

    def get_image_url(self, obj):
        req = self.context.get('request')
        if obj.image_url:
            return obj.image_url
        if obj.featured_image:
            return req.build_absolute_uri(obj.featured_image.url)
        return None

class HotelDetailSerializer(serializers.ModelSerializer):
    uid       = serializers.UUIDField(read_only=True)
    image_url = serializers.SerializerMethodField()
    rooms     = serializers.SerializerMethodField()

    class Meta:
        model  = Hotel
        fields = [
            'uid','name','location','description',
            'price','stars','amenities','image_url','rooms'
        ]

    def get_image_url(self, obj):
        req = self.context.get('request')
        if obj.image_url:
            return obj.image_url
        if obj.featured_image:
            return req.build_absolute_uri(obj.featured_image.url)
        return None

    def get_rooms(self, obj):
        qs = obj.rooms.filter(is_available=True)
        from .serializers import RoomSerializer
        return RoomSerializer(qs, many=True, context=self.context).data

class RoomSerializer(serializers.ModelSerializer):
    uid       = serializers.UUIDField(read_only=True)
    hotel     = serializers.UUIDField(source='hotel.uid', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = Room
        fields = [
            'uid','hotel','name','description',
            'bed_count','bathroom_count','bed_type',
            'price','capacity','is_available','image_url'
        ]

    def get_image_url(self, obj):
        req = self.context.get('request')
        if obj.image:
            return req.build_absolute_uri(obj.image.url)
        return None

class BookingSerializer(serializers.ModelSerializer):
    uid          = serializers.UUIDField(read_only=True)
    room_details = RoomSerializer(source='room', read_only=True)
    user         = serializers.PrimaryKeyRelatedField(
                       read_only=True,
                       default=serializers.CurrentUserDefault()
                   )

    class Meta:
        model  = Booking
        fields = [
            'uid','user','hotel','room','room_details',
            'check_in','check_out','status','total_price','created_at'
        ]
        read_only_fields = ['uid','status','user','created_at']

    def validate(self, data):
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError({'check_out':'Must be after check-in'})
        if data['room'] and not data['room'].is_available:
            raise serializers.ValidationError({'room':'Not available'})
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, style={'input_type':'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type':'password'})

    class Meta:
        model  = User
        fields = ['id','username','email','password','password2','is_admin','phone']
        extra_kwargs = {
            'is_admin': {'read_only':True},
            'phone': {'required':False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password':'Passwords must match'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_admin=validated_data.get('is_admin',False),
            phone=validated_data.get('phone','')
        )
