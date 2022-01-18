import argparse
import sys

from bs4 import BeautifulSoup
import requests
import unidecode


URL = 'https://cestina-pro-cizince.cz/trvaly-pobyt/a2/online-prihlaska/'


def _get_data(url=URL, tag='div', cls='town'):
    resp = requests.get(url)
    if resp.ok:
        html = resp.text
    soup = BeautifulSoup(html, features="lxml")
    return [e.text.split() for e in soup.find_all(tag) if getattr(e, tag) and cls in getattr(e, tag)["class"]]


def get_schools(fetched_data=_get_data()):
    res = {}
    # Sometimes the name of a town consists of several words, account for that
    for city_info in fetched_data:
        not_a_name_num, _ = next(((i, w) for (i, w) in enumerate(city_info) if w.startswith('(')), None)
        city_name = ' '.join(city_info[0: not_a_name_num])
        total_schools = int(city_info[not_a_name_num].lstrip('('))
        free_slots = city_info[-1] == 'Vybrat'
        status = city_info[-1]
        city_name_no_diacrytics = unidecode.unidecode(city_name)
        res[city_name_no_diacrytics] = {'free_slots': free_slots,
                                        'total_schools': total_schools,
                                        'status': status,
                                        'city_name': city_name}
    return res


def check_city(city, schools):
    no_diacrytics_city = unidecode.unidecode(city)
    if no_diacrytics_city not in schools:
        return sys.exit(f'No exams take place in {city}')
    city_czech_name = schools[no_diacrytics_city]['city_name']
    res = (f'Congratulations, there are free slots in {city_czech_name} :)'
           if schools[no_diacrytics_city]['free_slots'] else
           f'Try again later, no free slots in {city_czech_name} :(')
    print(res)
    return schools[no_diacrytics_city]


def parse_args(args, cities):
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', help='City to track exams in', choices=cities, action='append')
    return parser.parse_args(args)


if __name__ == "__main__":
    all_schools = get_schools()
    all_cities = sorted(c for c in all_schools)
    parsed_args = parse_args(sys.argv[1:], all_cities)
    cities = parsed_args.city or all_cities
    for a_city in cities:
        check_city(a_city, all_schools)
