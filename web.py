import json
import re
import sys
from urllib import parse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3 import Retry

api_url = "/api/houses"
base_url = "https://dom.mingkh.ru"


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

def get_coords_v2(house_id):
    r = requests.get(base_url + '/api/map/house/' + house_id)
    body = r.content.decode()
    data = json.loads(body)

    try:
        c = data.get('features')[0].get('geometry').get('coordinates')
        return {'lat': c[0], 'long': c[1]}
    except:
        return {'lat': 'Не задана', 'long': 'Не задана'}

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
    r = {
        'house_type': temp.get('Тип дома', "Нет данных"),
        'living_quarters': temp.get('Жилых помещений', "Нет данных"),
        'series_and_type_of_construction': temp.get('Серия, тип постройки', "Нет данных"),
        'type_of_overlap': temp.get('Тип перекрытий', "Нет данных"),
        'wall_material': temp.get('Материал несущих стен', "Нет данных"),
        'type_of_garbage_chute': temp.get('Тип мусоропровода', "Нет данных"),
        'recognized_as_emergency': temp.get('Дом признан аварийным', "Нет данных"),
        'playground': temp.get('Детская площадка', "Нет данных"),
        'sports_ground': temp.get('Спортивная площадка', "Нет данных"),
        'cadastral_number': temp.get('Кадастровый номер', "Нет данных")
    }

    # r['management_company'] = temp.get('Управляющая компания', "Нет данных")

    tables = soup.findAll('table')

    temp = {}
    for table in tables:
        for tr in table.findAll('tr'):
            try:
                _, k, v, _ = tr.text.split('\n')
                temp[k] = v
            except:
                pass

    r['additional_info'] = temp.get('Дополнительная информация', "Нет данных")
    r['energy_efficiency_class'] = temp.get('Класс энергетической эффективности', "Нет данных")
    r['least_number_of_floors'] = temp.get('Наименьшее количество этажей', "Нет данных")
    r['residential_area'] = temp.get('Площадь жилых помещений м2', "Нет данных")
    r['non_residential_area'] = temp.get('Площадь нежилых помещений м2', "Нет данных")
    r['common_area'] = temp.get('Площадь помещений общего имущества м2', "Нет данных")
    r['land_area_common_property'] = temp.get('Площадь зем. участка общего имущества м2', "Нет данных")
    r['parking_area'] = temp.get('Площадь парковки м2', "Нет данных")
    r['formation_of_capital_fund'] = temp.get('Формирование фонда кап. ремонта', "Нет данных")
    r['equipment'] = temp.get('Оборудование', "Нет данных")
    # r['management_company'] = temp.get('Несущие стены', "Нет данных")
    r['basement_area'] = temp.get('Площадь подвала, кв.м', "Нет данных")
    r['roof'] = temp.get('Крыша', "Нет данных")
    # r['garbage_chute'] = temp.get('Мусоропровод', "Нет данных")
    r['overlap'] = temp.get('Перекрытия', "Нет данных")
    r['facade'] = temp.get('Фасад', "Нет данных")
    r['foundation'] = temp.get('Фундамент', "Нет данных")
    r['number_of_house_entries'] = temp.get('Количество вводов в дом, ед.', "Нет данных")
    r['cesspit_volume'] = temp.get('Объем выгребных ям, куб. м.', "Нет данных")
    r['ventilation'] = temp.get('Вентиляция', "Нет данных")
    r['water_disposal'] = temp.get('Водоотведение', "Нет данных")
    r['gutter_system'] = temp.get('Система водостоков', "Нет данных")
    r['hot_gas_supply'] = temp.get('Газоснабжение', "Нет данных")
    r['hot_water_supply'] = temp.get('Горячее водоснабжение', "Нет данных")
    r['fire_extinguishing_system'] = temp.get('Система пожаротушения', "Нет данных")
    r['heat_supply'] = temp.get('Теплоснабжение', "Нет данных")
    r['cold_water_supply'] = temp.get('Холодное водоснабжение', "Нет данных")
    r['power_supply'] = temp.get('Электроснабжение', "Нет данных")

    # Remove spaces between float digits
    for key in r:
        r[key] = re.sub(r'(\d)\s+(\d)', r'\1\2', r.get(key))

    return r


def parse_house(house_url):
    additional_data = {}
    r = requests_retry_session().get(base_url + house_url)
    content = r.content.decode()

    # извлечение координат
    _, _, _, hid = house_url.split('/')
    coords = get_coords_v2(hid)
    additional_data.update(coords)

    # парсинг HTML страницы
    main_info = parse_html(content)
    additional_data.update(main_info)

    return additional_data
