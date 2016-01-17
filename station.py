#!/usr/bin/env python

import httplib
import sys
from bs4 import BeautifulSoup
import ipa_config

station_id = sys.argv[1]

def fetch_html(train_id):
    train_request = "/?p=station&id=" + train_id

    connection = httplib.HTTPConnection(ipa_config.domain)
    connection.request('GET', train_request)

    return connection.getresponse().read()

def get_simple_field(columns, index):
    field = columns[index].span.string
    return field.strip() if field else ''

def get_train_number(columns):
    contents = columns[0].span.a.contents
    number =  ' '.join(contents[0].split())
    if len(contents) > 2:
        name = contents[2].strip()
        return number + ' ' + name
    else:
        return number

def get_train_operator(columns):
    names = columns[1].span.a.string
    return names.strip() if names else ''

def get_train_date(columns):
    return get_simple_field(columns, 2)

def get_train_relation(columns):
    return get_simple_field(columns, 3)

def get_train_time(columns):
    return get_simple_field(columns, 4)

def get_train_delay(columns):
    return get_simple_field(columns, 5)

def parse_table(table):
    result = []
    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        if len(columns) > 0:
            result.append([
                get_train_number(columns),
                get_train_operator(columns),
                get_train_date(columns),
                get_train_relation(columns),
                get_train_time(columns),
                get_train_delay(columns),
            ])
    return result

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    arrivals, departures = soup.find_all('table')
    return parse_table(arrivals), parse_table(departures)

def print_station(rows):
    for row in rows:
        if (len(row) > 1):
            print ' | '.join(row)
        else:
            print row[0]


if __name__ == "__main__":
    html = fetch_html(station_id)
    arrivals, departues = parse_html(html)

    print 'PRZYJAZDY'
    print '---------------------------------'
    print_station(arrivals)

    print
    print
    print 'ODJAZDY'
    print '---------------------------------'
    print_station(departues)
