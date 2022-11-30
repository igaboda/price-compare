from unittest.mock import patch, MagicMock

import pytest
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from conftest import DATA_PATH, DRIVER_PATH
from scrapper.web_scrapper import Scrapper


SHOP_SOUP_PARSER = 'hebe'
SHOP_DRIVER_PARSER = 'superpharm'


@pytest.fixture
def webscrapper(db, load_shops, initialize_parser, request):
    parser = initialize_parser(request.param)
    scrapper = Scrapper([parser])
    return scrapper


def get_soup_mocked(search_url):
    print('--mocked soup--')
    search_url = f'{DATA_PATH}{SHOP_SOUP_PARSER}_test_data.txt'
    with open(search_url, 'rb') as fp:
        html = fp.read()

    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_driver_mocked(search_url):
    print('--mocked driver--')
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


@pytest.mark.parametrize('webscrapper', [SHOP_SOUP_PARSER], indirect=True)
@patch('scrapper.web_scrapper.Scrapper._get_soup',
       MagicMock(side_effect=get_soup_mocked))
def test_search_single_phrase_soup(load_shops, webscrapper):
    search_phrase = 'yope balsam'
    products = webscrapper.search_by_single_phrase(search_phrase)

    assert len(products) > 0
    assert 'name' in products[1]
    assert search_phrase == products[1]['search_phrase']


@pytest.mark.parametrize('webscrapper', [SHOP_DRIVER_PARSER], indirect=True)
@patch('scrapper.web_scrapper.Scrapper._get_webdriver',
       MagicMock(side_effect=get_driver_mocked))
def test_search_single_phrase_driver(load_shops, webscrapper):
    search_phrase = 'yope balsam'
    products = webscrapper.search_by_single_phrase(search_phrase)

    assert len(products) > 0
    assert 'name' in products[1]
    assert search_phrase == products[1]['search_phrase']
