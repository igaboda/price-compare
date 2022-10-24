from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from product.models import Product


class User(AbstractBaseUser):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'


class Favorite(models.Model):
    """Favorite products per user"""
    product_id = models.ManyToManyField(Product, related_name='favorites')
    user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favorites')
