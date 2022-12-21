import pytest
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from conftest import DATA_PATH, DRIVER_PATH
from scrapper.product_search import list_shop_parsers
from scrapper.shop_parser import get_shop_parser


@pytest.fixture
def load_html():
    """Factory function for reading html test data depending on shop."""
    def _load_html(shop, no_data=False):
        prefix = ''
        if no_data: prefix = 'no'
        with open(f'{DATA_PATH}{shop}_test_{prefix}data.txt', 'rb') as fp:
            html = fp.read()
        return html
    return _load_html


@pytest.fixture
def driver():
    """Launches chrome web driver."""
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')
    webdriver_config = {'service': Service(DRIVER_PATH), 'options': options}

    driver = webdriver.Chrome(**webdriver_config)
    return driver


def test_list_shop_parsers_when_shops_exist(db, load_shops):
    """Test product_search.list_shop_parsers function when shop data is loaded
    to the DB."""
    shop_parsers = list_shop_parsers()
    assert len(shop_parsers) == 3


def test_list_shop_parsers_is_empty_when_zero_shops(db):
    """Test product_search.list_shop_parsers function when shop data is missing
    from the DB."""
    shop_parsers = list_shop_parsers()
    assert len(shop_parsers) == 0


def test_get_shop_parser_for_not_implemented_shop_fails():
    """Test shop_parser.get_shop_parser for not implemented shop should raise
    error."""
    shop = 'notino'
    with pytest.raises(NotImplementedError) as e:
        get_shop_parser(shop)
    assert str(e.value) == 'Parser for given shop not implemented'


@pytest.mark.parametrize('shop', ['rossman', 'hebe'])
def test_soup_shop_parser_products_on_page(load_shops, load_html,
                                           initialize_parser, shop):
    """Test parse_data method of given shops with soup parser_type."""
    parser = initialize_parser(shop)

    html = load_html(shop)
    soup = BeautifulSoup(html, 'html.parser')

    parsed_data = parser.parse_data(soup)

    assert len(parsed_data) > 0
    assert 'name' in parsed_data[1]
    assert 'url' in parsed_data[1]


@pytest.mark.parametrize('shop', ['rossman', 'hebe'])
def test_soup_shop_parser_no_results_page(load_shops, load_html,
                                          initialize_parser, shop):
    """Test parse_data method of given shops with soup parser_type when
    search returns no results."""
    parser = initialize_parser(shop)

    html = load_html(shop, True)
    soup = BeautifulSoup(html, 'html.parser')

    parsed_data = parser.parse_data(soup)
    assert len(parsed_data) == 0


@pytest.mark.parametrize('shop', ['superpharm'])
def test_driver_shop_parser_products_on_page(load_shops, driver,
                                             initialize_parser, shop):
    """Test parse_data method of given shops with driver parser_type."""
    parser = initialize_parser(shop)

    html = f'file:///{DATA_PATH}{shop}_test_data.html'
    driver.get(html)

    parsed_data = parser.parse_data(driver)

    assert len(parsed_data) > 0
    assert 'name' in parsed_data[1]
    assert 'url' in parsed_data[1]


@pytest.mark.parametrize('shop', ['superpharm'])
def test_driver_shop_parser_no_results_page(load_shops, driver,
                                            initialize_parser, shop):
    """Test parse_data method of given shops with driver parser_type when
    search returns no results."""
    parser = initialize_parser(shop)

    html = f'file:///{DATA_PATH}{shop}_test_nodata.html'
    driver.get(html)

    parsed_data = parser.parse_data(driver)

    assert len(parsed_data) == 0

