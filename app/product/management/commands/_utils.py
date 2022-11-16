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
    shop_id = prod.pop('shop_id')
    shop = Shop.objects.get(id=shop_id)

    price = prod.pop('price')

    product = Product.objects.create(shop=shop, **prod)
    Price.objects.create(price=price, product=product)
