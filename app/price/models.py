from django.db import models
from simple_history.models import HistoricalRecords

from product.models import Product


class Price(models.Model):
    """Price of a product per shop"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, null=True)
    date = models.DateField(auto_now=True)
    price = models.FloatField()
    history = HistoricalRecords()

