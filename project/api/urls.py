from django.urls import path

from . import views
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("categories/", views.CategoryHandler, name="category_index"),
    path("categories/<int:category_id>/", views.CategoryDetailHandler, name="category_dom"),
    path("products/", views.ProductHandler, name="product_index"),
    path("products/<int:product_id>/", views.ProductDetailHandler, name="product_dom"),
] + debug_toolbar_urls()