from typing import Dict, Union

from shop.models import Shop
from product.models import Product
from price.models import Price


def shop_data_exists() -> bool:
    """Checks if shop data has already been loaded to the db."""
    shops = Shop.object.all()
    return len(shops) > 0


def product_exists(prod: Dict) -> Union['Product', None]:
    """Checks if product with given name and url already exists.
    If so, returns the product."""
    try:
        product = Product.objects.get(url=prod['url'])
    except Product.DoesNotExist:
        product = None
    return product


def create_product_from_dict(prod: Dict) -> 'Product':
    """Creates Product in database based on given dictionary."""
    shop_id = prod.pop('shop_id')
    shop = Shop.objects.get(id=shop_id)

    price = prod.pop('price')

    product = Product.objects.create(shop=shop, **prod)
    Price.objects.create(price=price, product=product)

    return product


def update_product_price(product: 'Product', prod_dict: Dict) -> 'Product':
    """Updates price of given product."""
    product.price.price = prod_dict['price']
    product.save()

    return product

