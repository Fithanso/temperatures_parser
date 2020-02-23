from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
import os.path
from .functions import *


def index(request):
    if not os.path.exists("parsed.db"):
        init_db()
    countries_list = get_countries()
    return render(request, 'temperature_parser/display_countries.html', {'countries': countries_list})


def country_detail(request, country):
    towns_list = get_towns(country)
    return render(request, 'temperature_parser/display_towns.html', {'towns': towns_list, 'country': country})


def town_detail(request, country, town):
    years_list = get_years()
    return render(request, 'temperature_parser/run_parsing.html', {'years': years_list, 'country': country, 'town': town})


def run_parsing(request, country, town):
    year = request.POST.get("year")
    month = request.POST.get("month")

    parse_month(country, town, month, year)
    redirect_url = reverse('success_page')

    return HttpResponseRedirect(redirect_url)


def success_page(request):
    return render(request, 'temperature_parser/success.html')


def save_countries(request):
    parse_countries()
    return render(request, 'temperature_parser/success.html')


def save_towns(request, country):
    parse_towns(country)
    return render(request, 'temperature_parser/success.html')


def save_years(request):
    parse_years()
    return render(request, 'temperature_parser/success.html')

