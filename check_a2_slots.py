"""
A helper script to track free A2 Czech language exam slots.
"""

import argparse
import csv
import datetime
import sys
import time

from bs4 import BeautifulSoup
import requests
import unidecode


URL = 'https://cestina-pro-cizince.cz/trvaly-pobyt/a2/online-prihlaska/'
# interval to wait before repeating the request
POLLING_INTERVAL = 15
CSV_FILENAME = 'out.csv'


def _get_data(url=URL, tag='div', cls='town'):
    try:
        resp = requests.get(url, headers={'Cache-Control': 'no-cache',
                                          'Pragma': 'no-cache',
                                          'User-agent': 'Mozilla/5.0'})
    except requests.exceptions.ConnectionError:
        return []
    if resp.ok:
        html = resp.text
        soup = BeautifulSoup(html, features="lxml")
        return [e.text.split() for e in soup.find_all(tag) if getattr(e, tag) and cls in getattr(e, tag)["class"]]
    return []


def get_schools(fetched_data=None):
    if not fetched_data:
        fetched_data = _get_data()
    res = {}
    timestamp = datetime.datetime.now().timestamp()
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
                                        'city_name': city_name,
                                        'timestamp': timestamp}
    return res


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


def parse_args(args, cities_choices):
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', help='City to track exams in', choices=cities_choices, action='append')
    parser.add_argument('--out', help='File to store json with schools data', default=CSV_FILENAME)
    return parser.parse_args(args)


if __name__ == "__main__":
    try:
        all_schools = get_schools()
        all_cities = sorted(c for c in all_schools)
        parsed_args = parse_args(sys.argv[1:], all_cities)
        cities = parsed_args.city or all_cities
        # show details for all cities
        for a_city in all_cities:
            pprint_city(a_city, all_schools)
        print(f"Will be tracking status in {cities}")
        write_csv(all_schools, cities, filename=parsed_args.out)

        old_data = all_schools
        while True:
            time.sleep(POLLING_INTERVAL)
            new_data = get_schools()
            if not new_data:
                # possibly not happy about scraper, wait and retry
                print("Looks like connection error, will try again later")
                continue
            print(f"Fetched data, available slots in {[c for c in new_data if new_data[c]['free_slots']]}")
            if any(old_data[c]['free_slots'] != new_data[c]['free_slots'] for c in cities):
                # show details for tracked cities
                for a_city in cities:
                    pprint_city(a_city, new_data, old_data)
                # update data
                write_csv(new_data, cities, filename=parsed_args.out)
                old_data = new_data
    except KeyboardInterrupt:
        sys.exit('Interrupted by user.')
