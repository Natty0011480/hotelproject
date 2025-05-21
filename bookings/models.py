import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email    = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    phone    = models.CharField(max_length=20, blank=True, null=True)

    # tell Django to use email instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Hotel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name           = models.CharField(max_length=200)
    location       = models.CharField(max_length=100)
    description    = models.TextField(blank=True)
    stars          = models.PositiveSmallIntegerField(
                        choices=[(i, f"{i}-star") for i in range(1,6)],
                        default=3
                     )
    amenities      = models.JSONField(default=list, help_text="Up to 5 amenities")
    image_url      = models.URLField(blank=True, null=True)
    has_pool       = models.BooleanField(default=False)
    has_gym        = models.BooleanField(default=False)
    price          = models.DecimalField(max_digits=10, decimal_places=2)
    is_active      = models.BooleanField(default=True)
    featured_image = models.ImageField(upload_to='hotel_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    hotel         = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    name          = models.CharField(max_length=100)
    description   = models.TextField(blank=True)
    bed_count     = models.PositiveSmallIntegerField(default=1)
    bathroom_count = models.PositiveSmallIntegerField(default=1)
    BED_TYPES      = [
        ('SINGLE', 'Single'),
        ('QUEEN',  'Queen Size'),
        ('KING',   'King Size'),
    ]
    bed_type       = models.CharField(max_length=10, choices=BED_TYPES, default='SINGLE')
    price         = models.DecimalField(max_digits=8, decimal_places=2)
    capacity      = models.PositiveIntegerField()
    is_available  = models.BooleanField(default=True)
    image         = models.ImageField(upload_to='room_images/', blank=True, null=True)

    def __str__(self):
        return self.name

class Booking(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    PENDING     = 'PENDING'; COMPLETED = 'COMPLETED'; CANCELLED = 'CANCELLED'
    STATUS_CHOICES = [(PENDING,'Pending'), (COMPLETED,'Completed'), (CANCELLED,'Cancelled')]

    hotel       = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    user        = models.ForeignKey(User,  on_delete=models.CASCADE)
    room        = models.ForeignKey(Room,  on_delete=models.CASCADE)
    check_in    = models.DateField()
    check_out   = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        # unique_together = ('room','check_in','check_out')

        # def __str__(self):
        #   return f"Booking #{self.uid}"
        pass

class Review(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    room       = models.ForeignKey(Room, on_delete=models.CASCADE)
    rating     = models.PositiveSmallIntegerField()
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review"
