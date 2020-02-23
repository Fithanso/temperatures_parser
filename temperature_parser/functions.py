import requests
from bs4 import BeautifulSoup as BS
import sqlite3

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def init_db():

    conn = sqlite3.connect("parsed.db")  # автоматически создает файл, если его нет
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE countries
                        (id integer PRIMARY KEY AUTOINCREMENT NOT NULL, name text, ru_name text)
                    """)

    cursor.execute("""CREATE TABLE towns
                        (id integer PRIMARY KEY AUTOINCREMENT NOT NULL, name text, ru_name text, ru_region text, region text, country text)
                    """)

    cursor.execute("""CREATE TABLE years
                        (id integer PRIMARY KEY AUTOINCREMENT NOT NULL, year integer)
                    """)

    cursor.execute("""CREATE TABLE temperatures
                        (id integer PRIMARY KEY AUTOINCREMENT NOT NULL, date integer, month text, year integer,
                         temp_day integer, temp_night integer, town text, country text)
                    """)
    return 0


# функция парсит названия всех стран
def parse_countries():
    url = 'https://world-weather.ru/pogoda/'
    r = requests.get(url, headers=headers)
    html = BS(r.text, 'html.parser')
    blocks = html.findAll('div', class_='block-cities')

    countries_result = []

    for block in blocks:
        for ul in block.select("ul"):
            for li in ul.findAll('li')[1:]:
                a = li.find('a')
                name = a['href'].split('/')[4]  # there are always five '/' symbols
                ru_name = a.text

                result_tuple = ()
                result_tuple = result_tuple + (name,)
                result_tuple = result_tuple + (ru_name,)
                countries_result.append(result_tuple)

    save('countries', countries_result)

    return countries_result


# функция парсит названия всех городов выбранной страны
def parse_towns(country):
    url = 'https://world-weather.ru/pogoda/{}/'.format(country)
    r = requests.get(url, headers=headers)
    html = BS(r.text, 'html.parser')

    city_block = html.findAll('li', class_='city-block')

    towns_result = []

    if not city_block:  # если разделено по регионам
        regions = html.findAll('ul', class_='cities reg')

        for region in regions:
            for li in region.select('li')[1:]:  # найти города в каждом регионе
                a = li.find('a')

                region_name = a['href'].split('/')[5]
                ru_region_name = a.text

                further_link = 'https://world-weather.ru/pogoda/{}/{}/'.format(country, region_name)  # ссылка на страницу региона с городами

                r = requests.get(further_link, headers=headers)
                html = BS(r.text, 'html.parser')

                towns = html.findAll('li', class_='city-block')

                for town in towns:  # парсим города
                    link = town.contents[0]
                    name = link.attrs['href'].split('/')[5]
                    ru_name = link.text

                    result_tuple = ()
                    result_tuple = result_tuple + (name,)
                    result_tuple = result_tuple + (ru_name,)
                    result_tuple = result_tuple + (ru_region_name,)
                    result_tuple = result_tuple + (region_name,)
                    result_tuple = result_tuple + (country,)
                    towns_result.append(result_tuple)

    else:  # делаем то же самое что и выше, но без захода в регионы
        towns = html.find_all('li', class_='city-block')

        for town in towns:  # парсим города

            link = town.contents[0]
            name = link.attrs['href'].split('/')[5]
            ru_name = link.text

            result_tuple = ()
            result_tuple = result_tuple + (name,)
            result_tuple = result_tuple + (ru_name,)
            result_tuple = result_tuple + (" ",)
            result_tuple = result_tuple + (" ",)
            result_tuple = result_tuple + (country,)
            towns_result.append(result_tuple)

    save('towns', towns_result)

    return towns_result


# функция парсит все доступные годы
def parse_years():
    url = 'https://world-weather.ru/pogoda/russia/moscow/february-2020/'  # ссылка на любую страницу с годами
    r = requests.get(url, headers=headers)
    html = BS(r.text, 'html.parser')
    div = html.find('div', class_='menu-years')

    years_result = []
    for a in div:

        year = a.text
        result_tuple = ()
        result_tuple = result_tuple + (year,)
        years_result.append(result_tuple)

    save('years', years_result)
    return years_result


# функция парсит значения дневных и ночных температур в течение месяца в выбранной (стране), городе, месяце и годе
def parse_month(country, town, month, year):
    url = 'https://world-weather.ru/pogoda/{}/{}/{}-{}/'.format(country, town, month, year)

    r = requests.get(url, headers=headers)

    html = BS(r.text, 'html.parser')
    ul = html.find('ul', class_='ww-month')

    days_result = []

    for li in ul:
        a = li.find('a')

        if a:
            date = a.find('div').text
            day_temp = a.find('span').text.replace('°', '')
            night_temp = a.find('p').text.replace('°', '')

            result_tuple = ()
            result_tuple = result_tuple + (date,)
            result_tuple = result_tuple + (month,)
            result_tuple = result_tuple + (year,)
            result_tuple = result_tuple + (day_temp,)
            result_tuple = result_tuple + (night_temp,)
            result_tuple = result_tuple + (town,)
            result_tuple = result_tuple + (country,)
            days_result.append(result_tuple)

    save('temperatures', days_result)

    return days_result


# функция сохраняет данные в БД sqlite
def save(table, args):

    conn = sqlite3.connect("parsed.db")
    cursor = conn.cursor()

    str_arg = ''

    for i in args[0]:  # 0 элемент, только чтобы определить кол-во столбцов
        str_arg += " ?, "

    str_arg = str_arg[0:-2]

    query = """INSERT INTO {0} VALUES (NULL, {1})""".format(table, str_arg)

    cursor.executemany(query, args)
    conn.commit()


# функция берет из бд все страны
def get_countries():

    conn = sqlite3.connect("parsed.db")
    cursor = conn.cursor()

    sql = "SELECT * FROM countries"

    cursor.execute(sql)
    result = []
    for country in cursor.fetchall():
        result.append(country)  # получаем название страны на англ

    return result


# функция берет из бд все города
def get_towns(country):

    conn = sqlite3.connect("parsed.db")
    cursor = conn.cursor()

    sql = "SELECT * FROM towns WHERE country = '{}'".format(country)

    cursor.execute(sql)

    result = []
    for town in cursor.fetchall():
        result.append(town)  # получаем все города

    return result


# функция берет из бд все годы
def get_years():

    conn = sqlite3.connect("parsed.db")
    cursor = conn.cursor()

    sql = "SELECT * FROM years"

    cursor.execute(sql)

    result = []
    for town in cursor.fetchall():
        result.append(town)  # получаем все годы

    return result




