import argparse
import asyncio
import csv
import datetime
import random
import sys

from bs4 import BeautifulSoup
import requests
import unidecode

URL = 'https://cestina-pro-cizince.cz/trvaly-pobyt/a2/online-prihlaska/'
# interval to wait before repeating the request
POLLING_INTERVAL = 15
CSV_FILENAME = 'out.csv'
LAST_FETCHED = 'last_fetched.html'


async def _do_fetch(url):
    try:
        resp = requests.get(url, headers={'Cache-Control': 'no-cache',
                                          'Pragma': 'no-cache',
                                          'User-agent': 'Mozilla/5.0'})
    except requests.exceptions.ConnectionError:
        return
    if resp.ok:
        return resp.text


def _html_to_list(html, tag, cls):
    """
    In case layout changes this function only has to be tuned to extract necessary data.
    Returned value is a dict with no-diacrytics-city-name used as keys
    """
    res = {}
    timestamp = datetime.datetime.now().timestamp()
    soup = BeautifulSoup(html, features="lxml")
    schools_data = [e.text.split() for e in soup.find_all(tag) if getattr(e, tag) and cls in getattr(e, tag)["class"]]
    # Sometimes the name of a town consists of several words, account for that
    for city_info in schools_data:
        not_a_name_num, _ = next(((i, w) for (i, w) in enumerate(city_info) if w.startswith('(')), None)
        city_name = ' '.join(city_info[0: not_a_name_num])
        total_schools = int(city_info[not_a_name_num].lstrip('('))
        free_slots = city_info[-1] == 'Vybrat'
        status = city_info[-1]
        city_name_no_diacrytics = unidecode.unidecode(city_name)
        res[city_name_no_diacrytics] = {'free_slots': free_slots,
                                        'total_schools': total_schools,
                                        'status': status,
                                        'city_name': city_name,
                                        'timestamp': timestamp}
    return res


async def fetch(url, filename=None):
    res = await _do_fetch(url=url)
    while not res:
        print("Looks like connection error, will try again later")
        await asyncio.sleep(random.randint(1, POLLING_INTERVAL))
        res = await _do_fetch(url=url)
    # record new data
    if filename:
        with open(filename, 'w') as f:
            f.write(res)
    return res


def get_schools_from_file(filename=LAST_FETCHED, tag='div', cls='town'):
    with open(filename) as f:
        html = f.read()
    return _html_to_list(html, tag, cls)


async def fetch_schools(url, filename=LAST_FETCHED, tag='div', cls='town'):
    html = await fetch(url, filename=filename)
    return _html_to_list(html, tag=tag, cls=cls)


def parse_args(args, cities_choices):
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', help='City to track exams in', choices=cities_choices, action='append')
    parser.add_argument('--out', help='File to store csv with schools data change over time', default=CSV_FILENAME)
    return parser.parse_args(args)


# XXX FIXME Has to go after debugging part done
def pprint_city(city, schools, prev_schools=None):
    no_diacrytics_city = unidecode.unidecode(city)
    city_czech_name = schools[no_diacrytics_city]['city_name']
    date = datetime.datetime.fromtimestamp(schools[no_diacrytics_city]['timestamp']).strftime('"%m/%d/%Y, %H:%M:%S"')
    if not prev_schools:
        # No information to compare with - provide data as is
        if no_diacrytics_city not in schools:
            sys.exit(f'No exams take place in {city}')
        res = (f'Congratulations, there are free slots in {city_czech_name} :)'
               if schools[no_diacrytics_city]['free_slots'] else
               f'Try again later, no free slots in {city_czech_name} :(')
    else:
        # Previous state is provided - keep track of changes only
        if schools[no_diacrytics_city]['free_slots'] != prev_schools[no_diacrytics_city]['free_slots']:
            res = (f'[{date}] Oops, no more free slots in {city_czech_name} :('
                   if not schools[no_diacrytics_city]['free_slots'] else
                   f'[{date}] Quick, book your exam in {city_czech_name}! :)')
    print(res)


def write_csv(schools, tracked_cities, filename=CSV_FILENAME):
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'free_slots', 'city']
        writer = csv.DictWriter(csvfile, fieldnames)
        for city in tracked_cities:
            no_diacrytics_city = unidecode.unidecode(city)
            writer.writerow({'timestamp': schools[no_diacrytics_city]['timestamp'],
                             'free_slots': schools[no_diacrytics_city]['free_slots'],
                             'city': schools[no_diacrytics_city]['city_name']})


async def main():
    # fetch initial data to set everything up (default choices for cities etc)
    schools = await fetch_schools(url=URL)
    all_cities = sorted(schools.keys())
    parsed_args = parse_args(sys.argv[1:], cities_choices=all_cities)
    cities = parsed_args.city or all_cities
    old_data = schools
    # XXX FIXME DEBUG show details for tracked cities
    for a_city in cities:
        pprint_city(a_city, old_data)
    try:
        while True:
            await asyncio.sleep(POLLING_INTERVAL)
            new_data = await fetch_schools(url=URL)
            # XXX FIXME DEBUG
            print(f"Fetched data, available slots in {[c for c in new_data if new_data[c]['free_slots']]}")
            if any(old_data[c]['free_slots'] != new_data[c]['free_slots'] for c in cities):
                # XXX FIXME DEBUG show details for tracked cities
                for a_city in cities:
                    pprint_city(a_city, new_data, old_data)
                # update data
                write_csv(new_data, cities, filename=parsed_args.out)
                old_data = new_data
    except KeyboardInterrupt:
        sys.exit('Interrupted by user.')


if __name__ == "__main__":
    asyncio.run(main())
