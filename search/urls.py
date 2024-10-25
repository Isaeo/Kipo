from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path("substitute/", views.find_substitute, name="substitute"),
    path("comparison/", views.compare_parts, name="comparison"),
    path("search", views.search_products, name="search"),
               ]
