import os

from web_scrapper import Scrapper
from shop_parser import get_shop_parser

# print(os.getcwd())
os.chdir('C:\\Users\\iboda\\PycharmProjects\\price-compare\\app\\scrapper')


search_phrases = (line.strip() for line in open('sample_search_phrases.txt'))
# search_phrases = ['yope balsam', ]

shops_dict = {
    'rossman': [
        'https://www.rossmann.pl/',
        'szukaj?Page=1&PageSize=96&Search={}',
        'soup'
    ],
    'hebe': [
        'https://www.hebe.pl/',
        'search?lang=pl_PL&q={}',
        'soup'
    ],
    'superpharm': [
        'https://www.superpharm.pl/',
        'catalogsearch/result/?categories=e-DROGERIA&q={}',
        'webdriver'
    ]
}

shops = []
for name, attr in shops_dict.items():
    shop_parser = get_shop_parser(name)
    shops.append(shop_parser(name, *attr))

scrapper = Scrapper(shops, search_phrases)
products = scrapper.search_by_phrases()
print(products)
