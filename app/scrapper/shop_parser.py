from typing import Union, Dict, List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


class ShopParser:
    """Base class for shop parser. Defines parse_data method for implementation
    in subclass."""

    def __init__(self, shop_id: int, shop_url: str, search_str: str,
                 parser_type: str):
        self.shop_id = shop_id
        self.url = shop_url
        self.search_str = search_str
        self.parser_type = parser_type

    def initialize_product(self, phrase: str) -> Dict[str, Union[int, str]]:
        """Creates product dictionary to be populated with further data."""
        product = {'shop_id': self.shop_id, 'search_phrase': phrase}
        return product

    def parse_data(self, *args):
        raise NotImplementedError('Method must be implemented')

    @staticmethod
    def check_product_description(phrase: str, description: str) -> bool:
        """Checks if all words from search phrase are included in product
        description."""
        phrase_list = phrase.split()
        desc_list = description.split()

        included = 0
        for ph in phrase_list:
            if ph in desc_list: included += 1

        check = True if included == len(phrase_list) else False
        return check


class RossmanParser(ShopParser):
    """Parser for extracting Rossman shop data from BeautifulSoup object."""
    shop_name = 'rossman'

    def parse_data(self, soup: BeautifulSoup, phrase: str = '') -> List[Dict]:
        """Extracts data from html elements for all products in soup.
        Returns data per each product in list of dictionaries."""
        prod_els = soup.select('.tile-product')
        empty_els = soup.select('.skeleton')

        if len(prod_els) == len(empty_els):
            return []

        result_caption = soup.select('h4')[0]
        if 'brak' in result_caption.text.lower():
            return []

        all_products = []
        for el in prod_els:
            if 'skeleton' in el.attrs['class']:
                continue

            product = self.initialize_product(phrase)
            product['shop_name'] = self.shop_name

            prod_children = el.select_one('[class*=name]').findChildren()
            product['name'] = prod_children[0].text.lower()
            # prod_desc = prod_children[1].text
            product['description'] = prod_children[1] \
                .contents[0].strip().strip(',').lower()
            # size extraction
            try:
                product['size'] = prod_children[2].text
            except IndexError:
                product['size'] = ''
            # price extraction
            prices_children = el.select_one('[class*=price]').findChildren()
            prices_children = [
                price.text.replace('zł', '').replace(',', '.').strip()
                for price in prices_children if price.text
            ]
            product['price'] = float(min(prices_children))
            # remaining fields
            product['image_url'] = el.find('img')['src']
            product['url'] = el.find('a')['href']

            all_products.append(product)

        return all_products


class HebeParser(ShopParser):
    """Parser for extracting Hebe shop data from BeautifulSoup object."""
    shop_name = 'hebe'

    def parse_data(self, soup: BeautifulSoup, phrase: str = '') -> List[Dict]:
        """Extracts data from html elements for all products in soup.
        Returns data per each product in list of dictionaries."""
        prod_els = soup.select('.product-tile')
        if not prod_els:
            return []

        all_products = []
        for el in prod_els:
            product = self.initialize_product(phrase)
            product['shop_name'] = self.shop_name

            product['name'] = el.select_one('[class*=name]') \
                .text.strip().lower()
            # description & size extraction
            prod_desc = el.select_one('.tooltip__content') \
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


class SuperpharmParser(ShopParser):
    """Parser for extracting Superpharm shop data from search url.
    Uses Chrome webdriver."""
    shop_name = 'superpharm'

    def parse_data(self, driver: webdriver, phrase: str = '') -> List[Dict]:
        """Extracts data from html elements for all products loaded on page."""
        # page = driver.page_source
        # f = codecs.open(f'{os.getcwd()}/tests/data/superpharm_test_nodata.html',
        #                 'w', encoding='utf-8')
        # f.write(page)

        result_caption = driver.find_element(
            By.CLASS_NAME, 'products-count-up'
        ).text.replace('(', '')
        if result_caption[:2] == '0 ':
            return []

        prod_els = driver.find_elements(By.CLASS_NAME, 'result-content')
        if not prod_els:
            return []

        all_products = []
        for el in prod_els:
            product = self.initialize_product(phrase)
            product['shop_name'] = self.shop_name

            product['name'] = el.find_element(
                By.CLASS_NAME, 'result-title').text.lower()
            product['description'] = el.find_element(
                By.CLASS_NAME, 'result-description').text.lower()

            # additional check to narrow down broad search results
            prod_desc = product['name'] + ' ' + product['description']
            if not self.check_product_description(phrase, prod_desc):
                continue

            # price extraction
            prod_price = el.find_element(
                By.CLASS_NAME, 'price-wrapper') \
                .find_element(By.CLASS_NAME, 'after_special').text
            prod_price = prod_price.replace(',', '.') \
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

        driver.close()

        return all_products


def get_shop_parser(name: str) -> Union['RossmanParser', 'HebeParser',
                                        'SuperpharmParser', None]:
    parser_mapping = {
        'rossman': RossmanParser,
        'hebe': HebeParser,
        'superpharm': SuperpharmParser
    }
    parser = parser_mapping.get(name.lower())
    if parser is None:
        raise NotImplementedError('Parser for given shop not implemented')

    return parser
