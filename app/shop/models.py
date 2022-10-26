from django.db import models


class Shop(models.Model):
    """Shop object"""
    shop_name = models.CharField(max_length=255)
    shop_url = models.CharField(max_length=255)

