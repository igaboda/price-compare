from django.db import models


class ShopParserType(models.TextChoices):
    SOUP = 'soup'
    WEBDRIVER = 'webdriver'


class Shop(models.Model):
    """Shop object"""
    shop_name = models.CharField(max_length=255)
    shop_url = models.CharField(max_length=255)
    search_param = models.CharField(max_length=255)
    parser_type = models.CharField(choices=ShopParserType.choices,
                                   max_length=20)

