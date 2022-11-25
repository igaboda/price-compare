import os
from typing import Union, Tuple, Dict, List

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from pandas import DataFrame


class Scrapper:
    """Webscrapper object for scrapping shop urls for given search phrases
    or scrapping specific product url.
    Should be used together with specific ShopParser objects"""

    # _driver_path = 'C:/Users/iboda/Downloads/chromedriver_win32/chromedriver.exe'
    _driver_path = '/usr/local/bin/chromedriver'

    def __init__(self, shops: List['Shop'],
                 search_phrases: Union[Tuple, List] = []):
        self.shops = shops
        self.search_phrases = search_phrases
        self.products = []
        self.path_to_save = '/tests/data/'

    def _find_shop_by_id(self, _id):
        """Iterates through list of shops to find the one with specified id."""
        shop = [sh for sh in self.shops if sh.shop_id == _id][0]
        return shop

    def _get_response_text(self, url: str) -> str:
        """Retrieves response from requested url."""
        with requests.get(url) as response:
            resp_txt = response.text
        return resp_txt

    def _save_response_to_file(self, resp_txt: str, file_name: str) -> None:
        """Saves response text to file for later testing."""
        with open(f'{os.getcwd()}{self.path_to_save}{file_name}.txt', 'w',
                  encoding='utf-8') as file:
            file.write(resp_txt)

    def _get_soup(self, url: str) -> BeautifulSoup:
        """Generates BeautifulSoup object based on response text of
        given url."""
        resp_txt = self._get_response_text(url)
        soup = BeautifulSoup(resp_txt, features='html.parser')
        return soup

    def _webdriver_config(self) -> Dict:
        """Returns chrome webdriver options and service."""
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        return {'service': Service(self._driver_path), 'options': options}

    def _transform_searched_data(self, prod_search_results: List[Dict]):
        """Processes raw data from search results. Returns cleaned and
        sorted list of products."""
        df_products = DataFrame(prod_search_results)
        df_products['name_to_sort'] = df_products[['name', 'description']] \
            .apply(lambda row: ' '.join(row.values), axis=1) \
            .str.replace(' |,|\+|-|', '')
        sort_order = ['search_phrase', 'name_to_sort', 'shop_id']
        df_products = df_products.sort_values(by=sort_order)\
            .drop(['search_phrase', 'name_to_sort'], axis=1)
        return df_products.to_dict('records')

    def search_by_single_phrase(self, phrase: str) -> List[Dict]:
        """Searches each shop for given phrase.
         Returns list of found products per each shop."""
        prod_all_shops = []

        for shop in self.shops:
            search_url = shop.url + \
                         shop.search_str.format(phrase.replace(' ', '%20'))
            print(search_url)

            if shop.parser_type == 'soup':
                soup = self._get_soup(search_url)
                products = shop.parse_data(soup, phrase)
            elif shop.parser_type == 'webdriver':
                webdriver_dict = self._webdriver_config()
                products = shop.parse_data(search_url, webdriver_dict, phrase)

            prod_all_shops.extend(products)

        return prod_all_shops

    def search_by_phrases(self) -> List[Dict]:
        """Searches each shop for each phrase in list. Returns list of found
        products for all searched phrases."""
        if self.search_phrases:
            prod_search_results = []
            for s_phrase in self.search_phrases:
                products = self.search_by_single_phrase(s_phrase)
                prod_search_results.extend(products)

            self.products = self._transform_searched_data(prod_search_results)

        return self.products





