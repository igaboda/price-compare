from typing import Dict

from shop.models import Shop
from product.models import Product
from price.models import Price


def shop_data_exists() -> bool:
    """Checks if shop data has already been loaded to the db."""
    shops = Shop.object.all()
    return len(shops) > 0

def product_data_exists(prod: Dict) -> bool:
    """Checks if product with given name and url already exists."""
    exists = Product.objects.filter(name=prod['name'], url=prod['url']).exists()
    return exists


def create_product_from_dict(prod: Dict) -> None:
    """Creates Product in database based on given dictionary."""
    shop = Shop.objects.get(id=prod['shop_id'])
    product = Product.objects.create(
        name=prod['name'],
        description=prod['description'],
        size=prod['size'],
        url=prod['url'],
        image_url=['image_url'],
        shop=shop
    )
    Price.objects.create(
        price=prod['price'],
        product=product
    )