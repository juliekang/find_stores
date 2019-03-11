#!/usr/bin/env python
import secrets
import argparse
import json
import urllib2
import sqlite3
from math import radians, cos, sin, asin, sqrt

def get_geocode(address, api_key):
    '''
    sample input:
        address='1770 Union St, San Francisco, CA 94123'
        api_key='ASDF'

    API endpoint format:
        https://maps.googleapis.com/maps/api/geocode/outputFormat?parameters

    sample output:
        (37.7981539, -122.4284318)
    '''
    api_call = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(address.replace(' ', '+'), api_key)
    try:
        response = str(urllib2.urlopen(api_call).read())
    except:
        return 'Something is wrong with the Google Maps API. Please try again.'
    else:
        result = json.loads(response.replace('\\n', ''))
        if result['status'] == 'OK':
            return (result['results'][0]['geometry']['location']['lat'], result['results'][0]['geometry']['location']['lng'])
        else:
            return 'Invalid address. Please try again.'

def closest_store(customer_geocode, units, cursor):
    '''
    sample input:
        customer_geocode=(45.0521539, -93.364854)
        units='mi'
        cursor=cursor connected to a sqlite3 database

    sample output: {
        'county': u'Utah County',
        'city': u'Orem',
        'state': u'UT',
        'name': u'Orem State Street',
        'zip': u'84057-4607',
        'address': u'175 W Center St',
        'latitude': 40.2952422,
        'distance': 17.407120020801525,
        'units': u'mi',
        'longitude': -111.6990958,
        'location': u'SWC Center St & Orem Blvd'
    }
    '''
    min_distance = None
    min_store = None
    for store in cursor.execute('SELECT * FROM stores'):
        current_store = {
            'name': store[0],
            'location': store[1],
            'address': store[2],
            'city': store[3],
            'state': store[4],
            'zip': store[5],
            'latitude': float(store[6]),
            'longitude': float(store[7]),
            'county': store[8],
            'distance': None,
            'units': units
        }
        store_geocode = (current_store['latitude'], current_store['longitude'])
        distance = calculate_distance(customer_geocode, store_geocode, units)
        if distance < min_distance or not min_distance:
            min_distance = current_store['distance'] = distance
            min_store = current_store

    return min_store

def calculate_distance(customer_geocode, store_geocode, units):
    '''
    sample input:
        customer_geocode=(37.7981539, -122.4284318)
        store_geocode=(37.7981539, -122.4284318)
        units='mi'

    sample output: 0
    '''
    customer_lat, customer_long = customer_geocode
    store_lat, store_long = store_geocode

    return haversine(customer_long, customer_lat, store_long, store_lat, units)

def haversine(lon1, lat1, lon2, lat2, units):
    """
    Utility function found here, adapted to give choice of km or miles:
    https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956 if units == 'mi' else 6371
    return c * r

def format_output(store, format):
    if format == 'text':
        return 'Your nearest store is {} {} away in {}. Please visit us at {}, {}, {} {}.'.format(
            round(store['distance'], 1),
            store['units'],
            store['name'],
            store['address'],
            store['city'],
            store['state'],
            store['zip']
        )
    else:
        return json.dumps(store)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Returns nearest store from user-given address or zip code.')
    # make sure user inputs address or zip
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--address', type=str,
                        help='Address of your starting point, format: "1770 Union St, San Francisco, CA 94123"')
    group.add_argument('--zip',type=str,
                        help='Zipcode of your starting point')

    parser.add_argument('--units', type=str, default = 'mi',
                        help='mi|km')
    parser.add_argument('--output', type=str, default = 'text',
                        help='text|json')

    args = parser.parse_args()

    #type checking
    if args.units != 'mi' and args.units != 'km':
        raise argparse.ArgumentTypeError("%s is invalid. units must be mi or km. " % args.units)
    if args.output != 'text' and args.output != 'json':
        raise argparse.ArgumentTypeError("%s is invalid. output format must be text or json. " % args.output)

    #connect to database created from store-locations.csv
    database = "stores.db"
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # grab api_key
    api_key = secrets.API_KEY

    # get geocode of --address or --zip
    address = args.address if args.address else args.zip
    user_geocode = get_geocode(address, api_key)

    # return result
    closest = closest_store(user_geocode, args.units, c)

    # format according to units and output format
    message = format_output(closest, args.output)
    print message
