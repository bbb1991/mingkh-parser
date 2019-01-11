import json
import re
import sys
from urllib import parse

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

api_url = "/api/houses"
base_url = "http://dom.mingkh.ru"


def get_payload(state, city=None):
    payload = {
        "current": 1,
        "rowCount": -1,
        "searchPhrase": "",
        "region_url": state
    }
    if city:
        payload.update({'city': city})
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


def get_houses(state, city=None):
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


def parse_house(house_url):
    additional_data = {}
    r = requests_retry_session().get(base_url + house_url)
    content = r.content.decode()

    # извлечение координат
    coords = get_coords(content)
    additional_data.update(coords)

    # TODO извлечение доп данных

    return additional_data
