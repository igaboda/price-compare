from django.db import models
from shop.models import Shop


class ProductGroup(models.Model):
    """Group of the same products"""
    product_group = models.CharField(max_length=255)


class Product(models.Model):
    """Product object"""
    product_name = models.CharField(max_length=255)
    product_description = models.CharField(max_length=255)
    size = models.CharField(max_length=100)
    product_url = models.CharField(max_length=255)
    shop = models.ForeignKey(Shop, null=True, on_delete=models.SET_NULL,
                             related_name='shops')
    product_group = models.ForeignKey(ProductGroup, null=True,
                                      on_delete=models.DO_NOTHING,
                                      related_name='product_groups')

    def __str__(self):
        return self.product_name




