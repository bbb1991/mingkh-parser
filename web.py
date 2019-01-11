import json
import re
import sys
from urllib import parse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3 import Retry

api_url = "/api/houses"
base_url = "http://dom.mingkh.ru"


def get_payload(state, city):
    payload = {
        "current": 1,
        "rowCount": -1,
        "searchPhrase": "",
        "region_url": state
    }
    if city:
        payload.update({'city_url': city})
    return payload


def requests_retry_session(
        retries=25,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_houses(state, city):
    payload = get_payload(state, city)
    r = requests.post(base_url + api_url, data=payload)
    if r.status_code != 200:
        print("Something went wrong! Status code is: {}".format(r.status_code))
        sys.exit(-1)
    body = r.content.decode()
    data = json.loads(body)
    return data


def get_coords(text):
    """
    Извлечение координат из скачанного html
    :param text: html
    :return: dict с ключами coord_x, coord_y
    """
    yandex_map_url = re.findall("panoramas.api-maps.yandex.ru.*$", text, re.MULTILINE)
    try:
        coords = dict(parse.parse_qsl(parse.urlsplit(yandex_map_url[0]).query)).get('ll').split(',')
        return {'coord_x': coords[0], 'coord_y': coords[1]}
    except IndexError as e:
        return {'coord_x': 'Не задана', 'coord_y': 'Не задана'}


def parse_html(text):
    soup = BeautifulSoup(text, 'html.parser')
    info = soup.find('dl')

    keys = []
    values = []
    for table in info.find_all('dt'):
        keys.append(table.text)
    for table in info.find_all('dd'):
        values.append(table.text)

    temp = dict(zip(keys, values))
    r = {}

    r['house_type'] = temp.get('Тип дома')
    r['living_quarters'] = temp.get('Жилых помещений')
    r['series_and_type_of_construction'] = temp.get('Серия, тип постройки')
    r['type_of_overlap'] = temp.get('Тип перекрытий')
    r['wall_material'] = temp.get('Материал несущих стен')
    r['type_of_garbage_chute'] = temp.get('Тип мусоропровода')
    r['recognized_as_emergency'] = temp.get('Дом признан аварийным')
    r['playground'] = temp.get('Детская площадка')
    r['sports_ground'] = temp.get('Спортивная площадка')
    r['cadastral_number'] = temp.get('Кадастровый номер')
    # r['management_company'] = temp.get('Управляющая компания')

    tables = soup.findAll('table')

    temp = {}
    for table in tables:
        for tr in table.findAll('tr'):
            try:
                _, k, v, _ = tr.text.split('\n')
                temp[k] = v
            except:
                pass

    print(temp)
    r['additional_info'] = temp.get('Дополнительная информация')
    r['energy_efficiency_class'] = temp.get('Класс энергетической эффективности')
    r['least_number_of_floors'] = temp.get('Наименьшее количество этажей')
    r['residential_area'] = temp.get('Площадь жилых помещений м2')
    r['non_residential_area'] = temp.get('Площадь нежилых помещений м2')
    r['common_area'] = temp.get('Площадь помещений общего имущества м2')
    r['land_area_common_property'] = temp.get('Площадь зем. участка общего имущества м2')
    r['parking_area'] = temp.get('Площадь парковки м2')
    r['formation_of_capital_fund'] = temp.get('Формирование фонда кап. ремонта')
    r['equipment'] = temp.get('Оборудование')
    # r['management_company'] = temp.get('Несущие стены')
    r['basement_area'] = temp.get('Площадь подвала, кв.м')
    r['roof'] = temp.get('Крыша')
    # r['garbage_chute'] = temp.get('Мусоропровод')
    r['overlap'] = temp.get('Перекрытия')
    r['facade'] = temp.get('Фасад')
    r['foundation'] = temp.get('Фундамент')
    r['number_of_house_entries'] = temp.get('Количество вводов в дом, ед.')
    r['cesspit_volume'] = temp.get('Объем выгребных ям, куб. м.')
    r['ventilation'] = temp.get('Вентиляция')
    r['water_disposal'] = temp.get('Водоотведение')
    r['gutter_system'] = temp.get('Система водостоков')
    r['hot_gas_supply'] = temp.get('Газоснабжение')
    r['hot_water_supply'] = temp.get('Горячее водоснабжение')
    r['fire_extinguishing_system'] = temp.get('Система пожаротушения')
    r['heat_supply'] = temp.get('Теплоснабжение')
    r['cold_water_supply'] = temp.get('Холодное водоснабжение')
    r['power_supply'] = temp.get('Электроснабжение')


    return r


def parse_house(house_url):
    additional_data = {}
    r = requests_retry_session().get(base_url + house_url)
    content = r.content.decode()

    # извлечение координат
    coords = get_coords(content)
    additional_data.update(coords)

    main_info = parse_html(content)
    additional_data.update(main_info)

    return additional_data
