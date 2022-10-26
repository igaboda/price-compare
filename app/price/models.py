from django.db import models
from simple_history.models import HistoricalRecords

from shop.models import Shop
from product.models import Product


class Price(models.Model):
    """Price of a product per shop"""
    product = models.ManyToManyField(Product)
    date = models.DateField(auto_now=True)
    price = models.FloatField()
    shop = models.ManyToManyField(Shop)
    product_url = models.CharField(max_length=255)
    history = HistoricalRecords()

