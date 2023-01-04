from unittest.mock import patch, call

import pytest
import requests
import responses
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from libs.utils import read_json_file
from conftest import DATA_PATH, DRIVER_PATH
from scrapper.web_scrapper import Scrapper
from scrapper.product_search import get_products_by_search_phrases


SHOP_SOUP_PARSER = 'hebe'
SHOP_DRIVER_PARSER = 'superpharm'
SHOPS = ['rossman', 'hebe', 'superpharm']
SEARCH_URLS = [
    'https://www.rossmann.pl/szukaj?Page=1&PageSize=96&Search={}',
    'https://www.hebe.pl/search?lang=pl_PL&q={}',
    'https://www.superpharm.pl/catalogsearch/result/?categories=e-DROGERIA&q={}'
]


@pytest.fixture
def webscrapper(db, load_shops, initialize_parser, request):
    """Creates Scrapper object for given shops."""
    shops = request.param
    parsers = [initialize_parser(shop) for shop in shops]
    scrapper = Scrapper(parsers)
    return scrapper


def get_soup_mocked(search_url):
    """Function for mocked Scrapper._get_soup method."""
    search_url = f'{DATA_PATH}{SHOP_SOUP_PARSER}_test_data.txt'
    with open(search_url, 'rb') as fp:
        html = fp.read()

    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_driver_mocked(search_url):
    """Function for mocked Scrapper._get_webdriver method."""
    search_url = f'file:///{DATA_PATH}{SHOP_DRIVER_PARSER}_test_data.html'

    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')
    webdriver_config = {'service': Service(DRIVER_PATH), 'options': options}

    driver = webdriver.Chrome(**webdriver_config)
    driver.get(search_url)
    return driver


@pytest.fixture(scope='module')
def search_phrases_test_data():
    """Reads search phrases test data from json file."""
    return read_json_file(f'{DATA_PATH}search_phrases_test_data.json')


def search_by_single_phrase_mocked(data):
    """Factory function for filtering data depending on search phrase."""
    return lambda s_phrase: [d for d in data if d['search_phrase'] == s_phrase]


@pytest.mark.parametrize('webscrapper', [[SHOP_SOUP_PARSER]], indirect=True)
@patch.object(Scrapper, '_get_soup', side_effect=get_soup_mocked)
def test_search_single_phrase_soup(mocked_soup, webscrapper):
    """Tests Scrapper.search_by_single_phrase method for soup parsers."""
    search_phrase = 'yope balsam'
    products = webscrapper.search_by_single_phrase(search_phrase)

    assert len(products) > 0
    assert 'name' in products[1]
    assert search_phrase == products[1]['search_phrase']


@pytest.mark.parametrize('webscrapper', [[SHOP_DRIVER_PARSER]], indirect=True)
@patch.object(Scrapper, '_get_webdriver', side_effect=get_driver_mocked)
def test_search_single_phrase_driver(mocked_driver, webscrapper):
    """Tests Scrapper.search_by_single_phrase method for driver parser."""
    search_phrase = 'yope balsam'
    products = webscrapper.search_by_single_phrase(search_phrase)

    assert len(products) > 0
    assert 'name' in products[1]
    assert search_phrase == products[1]['search_phrase']


@pytest.mark.parametrize('webscrapper', [SHOPS], indirect=True)
@patch('scrapper.web_scrapper.Scrapper.search_by_single_phrase')
def test_search_by_phrases(mocked_search, webscrapper, search_phrases_test_data):
    """Test Scrapper.search_by_phrases method for both parser types."""
    mocked_search.side_effect = search_by_single_phrase_mocked(
        search_phrases_test_data
    )

    search_phrases = ['yope balsam', 'himalaya pasta']
    webscrapper.search_phrases = search_phrases
    products = webscrapper.search_by_phrases()

    assert len(products) > 0
    calls = [call(search_phrases[0]), call(search_phrases[1])]
    mocked_search.assert_has_calls(calls)
    assert products[1]['shop_name'] in SHOPS


@pytest.mark.parametrize('webscrapper', [SHOPS], indirect=True)
@patch('scrapper.web_scrapper.Scrapper.search_by_single_phrase',
       return_value=[])
def test_search_by_phrases_no_data(mocked_search, webscrapper):
    """Test Scrapper.search_by_phrases method when no search phrases
    are passed. Should return empty list of products."""
    products = webscrapper.search_by_phrases()

    assert len(products) == 0
    mocked_search.assert_not_called()


@responses.activate
@pytest.mark.parametrize('webscrapper', [SHOPS], indirect=True)
@pytest.mark.parametrize('search_url', SEARCH_URLS)
def test_successful_mocked_get_response(search_url, webscrapper):
    """Test successful mocked get response for all search urls."""
    search_phrase = 'yope balsam'
    url = search_url.format(search_phrase.replace(' ', '%20'))

    responses.add(responses.GET, url, body=f'{search_phrase} results',
                  status=200)
    resp = webscrapper._get_response_text(url)

    assert resp == f'{search_phrase} results'
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url


@responses.activate
@pytest.mark.parametrize('webscrapper', [SHOPS], indirect=True)
@pytest.mark.parametrize('search_url', SEARCH_URLS)
def test_failed_mocked_get_response(search_url, webscrapper):
    """Test failed mocked get response for all search urls."""
    search_phrase = 'yope balsam'
    url = search_url.format(search_phrase.replace(' ', '%20'))

    responses.add(responses.GET, url, status=504)
    resp = webscrapper._get_response_text(url)

    assert resp == ''
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url


@pytest.mark.parametrize('search_url', SEARCH_URLS)
def test_get_response(search_url):
    """Test responsiveness of search urls per shop."""
    search_phrase = 'yope balsam'
    response = requests.get(
        url=search_url.format(search_phrase.replace(' ', '%20')),
    )

    assert response.status_code == 200
    assert search_phrase in response.text


@patch('scrapper.web_scrapper.Scrapper.search_by_single_phrase')
def test_get_products_by_search_phrases(mocked_search, db, load_shops,
                                        search_phrases_test_data):
    """Test product_search.get_products_by_search_phrases function
    when search phrases are specified."""
    mocked_search.side_effect = search_by_single_phrase_mocked(
        search_phrases_test_data
    )

    search_phrases = ['yope balsam', 'himalaya pasta']
    products = get_products_by_search_phrases(search_phrases)

    assert len(products) > 0
    calls = [call(search_phrases[0]), call(search_phrases[1])]
    mocked_search.assert_has_calls(calls)
    assert products[1]['shop_name'] in SHOPS


@patch('scrapper.web_scrapper.Scrapper.search_by_single_phrase')
def test_get_products_by_search_phrases(mocked_search, db, load_shops,
                                        search_phrases_test_data):
    """Test product_search.get_products_by_search_phrases function
    when no search phrases are specified."""
    mocked_search.side_effect = search_by_single_phrase_mocked(
        search_phrases_test_data
    )

    products = get_products_by_search_phrases([])

    assert len(products) > 0
    mocked_search.assert_called_once()
    assert products[1]['shop_name'] in SHOPS

