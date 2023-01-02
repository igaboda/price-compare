from unittest.mock import patch, Mock

from django.urls import reverse

from product.models import Product
from libs.utils import read_json_file, create_product_from_dict

PRODUCT_DATA_PATH = '/app/product/tests/data/product_search_test_data.json'
PRODUCT_SEARCH_URL = reverse('product:product-search')
PRODUCT_LIST_URL = reverse('product:search-results')


def test_get_product_search(client):
    """Test get product search view."""
    response = client.get(PRODUCT_SEARCH_URL)
    assert response.status_code == 200


@patch('product.views.get_products_by_search_phrases')
def test_submit_product_search_create_new_products(
        mocked_products, client, db, load_shops
):
    """Tests submission of product search form. Products found in search will
    be created in database."""
    mocked_products.return_value = read_json_file(PRODUCT_DATA_PATH)

    search_phrase = 'yope balsam'
    response = client.post(
        PRODUCT_SEARCH_URL, {'search_phrase': search_phrase}
    )

    assert response.status_code == 302
    assert response['location'] == PRODUCT_LIST_URL

    created_products = client.session.get('searched_products')
    assert isinstance(created_products, list) is True
    assert len(created_products) == 15


@patch('product.views.get_products_by_search_phrases')
def test_submit_product_search_update_existing_products(
        mocked_products, client, db, load_shops
):
    """Tests submission of product search form for case when products found
    in search already exist in the database. Products should be updated."""
    products = read_json_file(PRODUCT_DATA_PATH)[:5]
    product_ids = []
    for product in products:
        db_product = create_product_from_dict(product)
        product_ids.append(db_product.id)

    updated_price = 30
    updated_products = products
    for prod in updated_products:
        prod.update(price=updated_price)
    mocked_products.return_value = updated_products

    search_phrase = 'yope balsam'
    response = client.post(
        PRODUCT_SEARCH_URL, {'search_phrase': search_phrase}
    )
    assert response.status_code == 302

    updated_db_products = client.session.get('searched_products')
    assert set(updated_db_products) == set(product_ids)

    db_products = Product.objects.all()
    for product in db_products:
        assert product.price.price == updated_price


def test_submit_product_search_invalid_form(client):
    """Tests submission of empty form. For invalid form response should render
    the same page (product search)."""
    response = client.post(PRODUCT_SEARCH_URL, {'search_phrase': ''})

    print(response.content)

    assert response.status_code == 200
    assert response.templates[0].name == 'product/product_search.html'


@patch('product.views.get_products_by_search_phrases', Mock(return_value=[]))
def test_submit_product_search_no_data(client, db, load_shops):
    """Tests the case when no products are found for submitted search phrase.
    No products will be created in the database."""
    search_phrase = 'bee natural pomadka'
    response = client.post(
        PRODUCT_SEARCH_URL, {'search_phrase': search_phrase}
    )
    assert response.status_code == 302
    assert response['location'] == PRODUCT_LIST_URL

    created_products = client.session.get('searched_products')
    assert len(created_products) == 0


