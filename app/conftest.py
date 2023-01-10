import pytest

from django.core.management import call_command

from scrapper.shop_parser import get_shop_parser
from shop.models import Shop


DATA_PATH = '/app/scrapper/tests/data/'
DRIVER_PATH = '/usr/local/bin/chromedriver'


@pytest.fixture
def load_shops(db):
    """Loads shops data to database."""
    call_command('loaddata', f'{DATA_PATH}shop_test_data.json')


@pytest.fixture
def initialize_parser(db):
    """Factory function for initializing given ShopParser object."""
    def _initialize_parser(shop):
        parser_obj = get_shop_parser(shop)
        shop_data = Shop.objects.defer('shop_name').get(shop_name=shop)
        parser = parser_obj(shop_data.id, shop_data.shop_url,
                            shop_data.search_param)
        return parser
    return _initialize_parser
