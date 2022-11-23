from django.urls import path
from product import views

urlpatterns = [
    path('product-search', views.ProductSearchView.as_view(),
         name='product-search'),
    path('product-search-results', views.ProductSearchResultsView.as_view(),
         name='search-results'),
    # path('products/<str:search_phrase', views.ProductsView.as_view(), name='products')
]