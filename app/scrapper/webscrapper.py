from typing import Tuple, Dict, List

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from pandas import DataFrame


class Scrapper:
    _driver_path = 'C:/Users/iboda/Downloads/chromedriver_win32/chromedriver.exe'
    # _driver_path = '/usr/local/bin/chromedriver'

    def __init__(self, search_phrases: Tuple, shops: List['Shop']):
        self.search_phrases = search_phrases
        self.shops = shops
        self.products = []

    def _get_response_text(self, url: str) -> str:
        """Retrieves response from requested url."""
        with requests.get(url) as response:
            resp_txt = response.text
        return resp_txt

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
        df_products['temp_name'] = df_products['name'].str.replace(' ', '')
        sort_order = ['search_phrase', 'temp_name', 'description', 'shop_name']
        df_products = df_products.sort_values(by=sort_order)
        ##
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
                products = shop.parser(soup, phrase)
            elif shop.parser_type == 'webdriver':
                webdriver_dict = self._webdriver_config()
                products = shop.parser(search_url, webdriver_dict, phrase)

            prod_all_shops.extend(products)

        return prod_all_shops

    def search_by_phrases(self) -> List[Dict]:
        """Searches each shop for each phrase in list. Returns list of found
        products for all searched phrases."""
        prod_search_results = []
        for s_phrase in self.search_phrases:
            products = self.search_by_single_phrase(s_phrase)
            prod_search_results.extend(products)

        self.products = self._transform_searched_data(prod_search_results)

        return self.products


class ShopParser:
    def __init__(self, shop_name: str, shop_url: str, search_str: str,
                 parser_type: str):
        self.name = shop_name
        self.url = shop_url
        self.search_str = search_str
        self.parser_type = parser_type
        setattr(self, 'parser', self.__getattribute__(f'{self.name}_parser'))

    @classmethod
    def rossman_parser(cls, soup: BeautifulSoup, phrase: str) -> List[Dict]:
        prod_els = soup.select('.tile-product')
        empty_els = soup.select('.skeleton')

        if len(prod_els) == len(empty_els):
            return []

        all_products = []
        for el in prod_els:
            if 'skeleton' in el.attrs['class']:
                continue

            product = cls.initialize_product('rossman', phrase)

            prod_children = el.select_one('[class*=name]').findChildren()
            product['name'] = prod_children[0].text.lower()
            # prod_desc = prod_children[1].text
            product['description'] = prod_children[1].contents[0].strip().strip(',').lower()
            # size extraction
            try:
                product['size'] = prod_children[2].text
            except IndexError:
                product['size'] = ''
            # price extraction
            prices_children = el.select_one('[class*=price]').findChildren()
            prices_children = [
                price.text.replace('zł', '').replace(',', '.').strip()
                for price in prices_children
            ]
            product['price'] = float(min(prices_children))
            # remaining fields
            product['image_url'] = el.find('img')['src']
            product['url'] = el.find('a')['href']

            all_products.append(product)

        return all_products

    @classmethod
    def hebe_parser(cls, soup: BeautifulSoup, phrase: str) -> List[Dict]:
        prod_els = soup.select('.product-tile')
        if not prod_els:
            return []

        all_products = []
        for el in prod_els:
            product = cls.initialize_product('hebe', phrase)

            product['name'] = el.select_one('[class*=name]')\
                .text.strip().lower()
            # description & size extraction
            prod_desc = el.select_one('.tooltip__content')\
                .select('.text--center')[-1].text.strip().split(',')
            product['description'] = prod_desc[0]
            product['size'] = prod_desc[-1].strip()
            # price extraction
            prod_pricing = el.select_one('[class*=price]')
            prod_price = prod_pricing.select_one('[class*=sales]') \
                .contents[0].strip()
            prod_price = prod_price + '.' + prod_pricing.select_one(
                '[class*=sales]').select_one('[class*=decimal]').text
            product['price'] = float(prod_price)
            # remaining fields
            product['image_url'] = el.find('img')['data-srcset'].split('?')[0]
            # srcset = ....png?sw=200&sh=200&sm=fit
            product['url'] = el.find('a')['href']

            all_products.append(product)

        return all_products

    @classmethod
    def superpharm_parser(cls, search_url: str, webdriver_config: Dict,
                          phrase: str,) -> List[Dict]:
        with webdriver.Chrome(**webdriver_config) as driver:
            # print(driver.capabilities['chrome']['chromedriverVersion'])
            driver.implicitly_wait(15)
            driver.get(search_url)
            # print(driver.current_url)
            # driver.find_element(By.ID, 'btn-cookie-allow').click()
            prod_els = driver.find_elements(By.CLASS_NAME, 'result-content')
            if not prod_els:
                return []

            all_products = []
            for el in prod_els:
                product = cls.initialize_product('superpharm', phrase)
                product['name'] = el.find_element(
                    By.CLASS_NAME, 'result-title').text.lower()
                product['description'] = el.find_element(
                    By.CLASS_NAME, 'result-description').text.lower()
                # price extraction
                prod_price = el.find_element(
                    By.CLASS_NAME, 'price-wrapper') \
                    .find_element(By.CLASS_NAME, 'after_special').text
                prod_price = prod_price.replace(',', '.')\
                    .replace(' zł', '')
                product['price'] = float(prod_price)
                # size extraction
                prod_size = el.find_element(
                    By.CLASS_NAME, 'custom-select-wrapper').text
                product['size'] = prod_size.split(':')[-1]
                # remaining fields
                prod_img = el.find_element(
                    By.CLASS_NAME, 'result-thumbnail')
                product['image_url'] = prod_img.find_element(
                    By.TAG_NAME, 'img').get_attribute('src')
                product['url'] = prod_img.find_element(
                    By.TAG_NAME, 'a').get_attribute('href')

                all_products.append(product)

        return all_products

    @staticmethod
    def initialize_product(shop_name: str, phrase: str) -> Dict[str, str]:
        product = {'shop_name': shop_name, 'search_phrase': phrase}
        return product



