from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import ListView
from django.urls import reverse

from product.forms import ProductSearchForm
from product.models import Product
from scrapper.product_search import get_products_by_search_phrases
from libs import utils


class ProductSearchView(View):
    """Handles product search form. Submission of form launches web scraper."""
    def get(self, request):
        form = ProductSearchForm()
        return render(request, 'product/product_search.html', {'form': form})

    def post(self, request):
        form = ProductSearchForm(request.POST)

        if form.is_valid():
            search_phrases = form.cleaned_data['search_phrase'].split(',')
            search_phrases = [s_ph.strip() for s_ph in search_phrases]

            products = get_products_by_search_phrases(search_phrases)

            prod_ids = []
            if products:
                for prod in products:
                    existing_product = utils.product_exists(prod)
                    if not existing_product:
                        print('create product')
                        product = utils.create_product_from_dict(prod)
                    else:
                        print('update product')
                        product = utils.update_product_price(
                            existing_product, prod
                        )
                    prod_ids.append(product.id)

            request.session['searched_products'] = prod_ids

            return HttpResponseRedirect(reverse('search-results'))

        return render(request, 'product/product_search.html', {'form': form})


class ProductSearchResultsView(ListView):
    """Displays search results - list of products found by scrapper."""
    template_name = 'product/product_list.html'
    model = Product
    context_object_name = 'products'

    def get_queryset(self):
        product_ids = self.request.session.get('searched_products', None)
        print(product_ids)
        data = None
        if product_ids:
            data = super().get_queryset().filter(id__in=product_ids)
        return data
