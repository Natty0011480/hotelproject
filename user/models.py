from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email    = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    phone    = models.CharField(max_length=20, blank=True, null=True)
    username = models.CharField(max_length=50, blank=False, null=False)

    # tell Django to use email instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']