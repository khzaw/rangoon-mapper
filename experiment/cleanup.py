import csv
import json
from itertools import groupby
from pprint import pprint
from operator import itemgetter

BLUE = '#405CAA'
RED = '#DF504E'
PURPLE = '#96509F'
ORANGE = '#E47B27'
BROWN = '#86603E'
GREEN = '#2C8A6C'

colors = {}
colors.update(colors.fromkeys([1, 11, 20, 21, 22, 23, 35, 36, 37, 39, 40, 41, 42, 61], BLUE));
colors.update(colors.fromkeys([2, 3, 4, 5, 6, 7, 12, 14, 15, 16, 17, 18, 19, 24, 25, 26, 27, 28, 29, 30, 38, 59], RED))
colors.update(colors.fromkeys([8, 9, 10, 31, 32, 33, 34], PURPLE))
# colors.update(colors.fromkeys([], ORANGE))
colors.update(colors.fromkeys([56, 57, 58], BROWN))
colors.update(colors.fromkeys(range(43, 56) + [60], GREEN))


print 'Creating all_bus_stops.json'
with open('bus_stops_by_service_000115.tsv') as f:
    reader = csv.reader(f, delimiter='\t')
    bus_stops = []
    for row in list(reader)[1:]:
        stop = {
            'service_name': int(row[0]),
            'sequence': int(row[1]),
            'bus_stop_id': int(row[2]),
            'name_en': row[3],
            'name_mm': row[4],
            'road_en': row[5],
            'road_mm': row[6],
            'township_en': row[7],
            'township_mm': row[8],
            'lat': float(row[9]),
            'lng': float(row[10]),
        }
        stop['color'] = colors[stop['service_name']]
        bus_stops.append(stop)

with open('all_bus_stops.json', 'wb') as f:
    f.write(json.dumps(bus_stops))

print 'Creating stops_map.json'
unique_stops = {}
for bus in bus_stops:
    if bus['bus_stop_id'] not in unique_stops:
        unique_stops[bus['bus_stop_id']] = {
            'name_en': bus['name_en'],
            'name_mm': bus['name_mm'],
            'road_en': bus['road_en'],
            'road_mm': bus['road_mm'],
            'township_en': bus['township_en'],
            'township_mm': bus['township_mm'],
            'lat': bus['lat'],
            'lng': bus['lng'],
            'services': [
                {
                    'service_name': bus['service_name'],
                    'sequence': bus['sequence'],
                    'color': colors[bus['service_name']]
                }
            ]
        }
    else:
        unique_stops[bus['bus_stop_id']]['services'].append({
            'service_name': bus['service_name'],
            'sequence': bus['sequence']
        })


print 'Creating unique_stop.json'
unique_stops_list = []
for id, value in unique_stops.iteritems():
    value['bus_stop_id'] = id
    unique_stops[id]['bus_stop_id'] = id
    unique_stops_list.append(value)

with open('stops_map.json', 'wb') as f:
    f.write(json.dumps(unique_stops))

with open('unique_stops.json', 'wb') as f:
    f.write(json.dumps(unique_stops_list))

print 'Loading all_bus_stops and unique_stops'
bus_stops = json.loads(open('unique_stops.json', 'rb').read())
bus_stops = sorted(bus_stops, key=itemgetter('bus_stop_id'))

all_bus_stops = json.loads(open('all_bus_stops.json', 'rb').read())
all_bus_stops = sorted(all_bus_stops, key=itemgetter('service_name'))


def compose(f, g):
    return lambda x: f(g(x))


def get_distance(lon1, lat1, lon2, lat2):
    from math import radians, cos, sin, asin, sqrt
    lon1, lat1, lon2, lat2 = map(compose(radians, float),
                                 [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km

print 'Creating bus_services.json'
bus_services = {}
services = groupby(all_bus_stops, key=itemgetter('service_name'))
for service_no, stops in services:
    bus_services[service_no] = {
        'color': colors[service_no],
        'stops': list(stops)
    }
with open('bus_services.json', 'wb') as f:
    f.write(json.dumps(bus_services))

print 'Creating adjacencyList.json'
graph = {}
services = groupby(all_bus_stops, key=itemgetter('service_name'))
for service_no, stops in services:
    stops = list(stops)
    for stop in stops[:-1]:
        key = stop['bus_stop_id']
        if key not in graph:
            graph[key] = []

        next_stop = stops[stops.index(stop) + 1]
        distance = get_distance(stop['lng'], stop['lat'],
                                next_stop['lng'], next_stop['lat'])
        assert distance >= 0, (stop, next_stop)
        next_stop['distance'] = distance
        graph[key] += [next_stop]

with open('adjancencyList.json', 'wb') as f:
    f.write(json.dumps(graph))
