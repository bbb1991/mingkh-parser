#!/usr/bin/python3

import argparse
import sys

import store
import web

parser = argparse.ArgumentParser(description='Script for parsing website dom.mingkh.ru')
parser.add_argument('-s', '--state', type=str, help='The name of the state, which data you want to retrieve')
parser.add_argument('-c', '--city', type=str,
                    help='The name of the city, which data you want to retrieve. Optional argument')
parser.add_argument('-l', '--list', action='store_true', help='Show list of available cities')


def show_cities(data):
    cities = set()
    for row in data.get('rows'):
        url = row.get('url')
        _, s, c, _ = url.split('/')
        cities.add(c)
    print("Available cities are: ")
    for i in cities:
        print(i)


if __name__ == '__main__':
    args = parser.parse_args()
    state = args.state
    list_cities = args.list
    if not state:
        print("At least state is required!")
        sys.exit(-1)
    city = args.city
    content = web.get_houses(state, city)
    if list_cities:
        show_cities(content)
        sys.exit(0)
    result = []
    for row in content.get('rows'):
        _, s, c, hid = row.get('url').split('/')
        print("Processing row with id: {}, house ID: {}, url: {}".format(row.get('rownumber'), hid, row.get('url')))
        url = row.get('url')
        extra_data = web.parse_house(url)
        row.update(extra_data)
        row.update({'state': s, 'city': c})
        result.append(row)

    print(len(result))
    store.save_result(result, state, city)
