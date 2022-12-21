from django.core.management.base import BaseCommand
from django.core.management import call_command

from libs import utils
from scrapper.product_search import get_products_by_search_phrases


class Command(BaseCommand):
    help = 'Populates Shops table. Generates sample products data and loads it to the database.'

    def add_arguments(self, parser):
        parser.add_argument('--search-phrase', required=False,
                            nargs='*', help='Initial data will be loaded for '
                                            'specified search phrase.')

    def handle(self, *args, **options):
        """Entrypoint for generate_initial_data command"""
        if not utils.shop_data_exists():
            self.stdout.write('Loading shop data...')
            call_command('loaddata', 'shop_data')

        search_phrases = options.get('search-phrase', [])
        if search_phrases:
            self.stdout.write(f'Searching for: {search_phrases}')

        products = get_products_by_search_phrases(search_phrases)

        if not products:
            return

        for prod in products:
            if not utils.product_exists(prod):
                self.stdout.write('Inserting product...')
                utils.create_product_from_dict(prod)
        self.stdout.write('Data load complete!')


