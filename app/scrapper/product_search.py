from typing import Union, Tuple, List, Dict

from scrapper.web_scrapper import Scrapper
from scrapper.shop_parser import get_shop_parser
from shop.models import Shop


SAMPLE_FILE = '/app/scrapper/sample_search_phrases.txt'


def list_shop_parsers():
    """Produce list of shop parsers based on shop objects."""
    shops = Shop.objects.all()
    shop_parsers = []
    for shop in shops:
        shop_parser = get_shop_parser(shop.shop_name)
        shop_parsers.append(shop_parser(shop.id, shop.shop_url,
                                        shop.search_param, shop.parser_type))
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


