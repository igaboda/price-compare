from django.db import models

from shop.models import Shop


class ProductGroup(models.Model):
    """Group of the same products"""
    product_group = models.CharField(max_length=255)


class Product(models.Model):
    """Product object"""
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    size = models.CharField(max_length=100)
    image_url = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE,
                             related_name='shops')
    product_group = models.ForeignKey(ProductGroup, null=True,
                                      on_delete=models.DO_NOTHING,
                                      related_name='product_groups')

    def __str__(self):
        return self.name








