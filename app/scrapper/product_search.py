from typing import Union, Tuple, List, Dict

from scrapper.web_scrapper import Scrapper
from scrapper.shop_parser import get_shop_parser
from libs.utils import update_product_price, get_product_url
from shop.models import Shop
from product.models import Product


SAMPLE_FILE = '/app/scrapper/sample_search_phrases.txt'


def list_shop_parsers():
    """Produce list of shop parsers based on shop objects."""
    shops = Shop.objects.all()
    shop_parsers = []
    for shop in shops:
        shop_parser = get_shop_parser(shop.shop_name)
        shop_parsers.append(shop_parser(shop.id, shop.shop_url,
                                        shop.search_param))
    return shop_parsers


def get_products_by_search_phrases(search_phrases: Union[Tuple, List, None]) -> Dict:
    """Launches web scrapper to gather products data for given search phrases.
    Returns search results as list of product dictionaries."""

    if not search_phrases:
        search_phrases = (line.strip() for line in
                          open(SAMPLE_FILE))

    shop_parsers = list_shop_parsers()

    scrapper = Scrapper(shop_parsers, search_phrases)
    products = scrapper.search_by_phrases()

    return products


def check_prices_of_products(products: List['Product'], update: bool = False) -> List:
    """Extracts current prices of given products. Returns list of products
    with lower current prices.
    If update parameter set to True price is updated in database."""
    shop_parsers = list_shop_parsers()

    scrapper = Scrapper(shop_parsers)

    lower_prices = []
    for product in products:
        prod_url = get_product_url(product)
        prod_price = product.price.price

        current_price = scrapper.get_price_of_single_product(
            prod_url, product.shop.id
        )

        if current_price != prod_price and update:
            product = update_product_price(product, {'price': current_price})

        if current_price < prod_price:
            lower_prices.append(product)

    return lower_prices





