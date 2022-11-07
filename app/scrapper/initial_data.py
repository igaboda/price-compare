import os

from scrapper.webscrapper import Scrapper, ShopParser

os.chdir('C:\\Users\\iboda\\PycharmProjects\\price-compare\\app\\scrapper')

search_phrases = (line.strip() for line in open('search_phrases.txt'))

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

shops = [ShopParser(name, *attr) for name, attr in shops_dict.items()]

scrapper = Scrapper(search_phrases, shops)
products = scrapper.search_by_phrases()
