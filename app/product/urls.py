from django.urls import path
from product import views

urlpatterns = [
    path('', views.ProductSearchView.as_view(),
         name='product-search'),
    path('search-results', views.ProductSearchResultsView.as_view(),
         name='search-results'),
]