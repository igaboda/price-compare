import pytest
from django.core.management import call_command

from scrapper.product_search import list_shop_parsers
from scrapper.shop_parser import get_shop_parser


@pytest.fixture
def load_shops(db) -> None:
    call_command('loaddata', '/app/scrapper/tests/data/shop_test_data.json')


def test_list_shop_parsers_when_shops_exist(db, load_shops):
    shop_parsers = list_shop_parsers()
    assert len(shop_parsers) == 3


def test_list_shop_parsers_is_empty_when_zero_shops(db):
    shop_parsers = list_shop_parsers()
    assert len(shop_parsers) == 0


def test_get_shop_parser_for_not_implemented_shop_fails():
    shop = 'notino'
    with pytest.raises(NotImplementedError) as e:
        get_shop_parser(shop)
    assert str(e.value) == 'Parser for given shop not implemented'