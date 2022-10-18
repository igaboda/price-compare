from django.db import models


class Product(models.Model):
    """Product object"""
    product_name = models.CharField(max_length=255, null=False)
    product_category = models.CharField(max_length=255)
    size = models.CharField(max_length=100)

    def __str__(self):
        return self.product_name

