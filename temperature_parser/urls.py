from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='countries_list_url'),
    path('success/', success_page, name='success_page'),
    path('parse/countries/', save_countries, name='parse_countries'),
    path('parse/towns/<str:country>/', save_towns, name='parse_towns'),
    path('parse/years/', save_years, name='parse_years'),
    path('country/<str:country>/', country_detail, name='country_detail_url'),
    path('<str:country>/<str:town>/', town_detail, name='town_detail_url'),
    path('<str:country>/<str:town>/parse/', run_parsing, name='run_parsing'),  # post request


]
