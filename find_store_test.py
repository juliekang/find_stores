import pytest
import find_store
import secrets

def test_get_geocode():
    assert find_store.get_geocode('1770 Union St, San Francisco, CA 94123', secrets.API_KEY) == (37.7981539, -122.4284318)

def test_haversine():
    km_value = find_store.haversine(100, 10, 200, 10, 'km')
    mi_value = find_store.haversine(100, 10, 200, 10, 'mi')
    assert float(km_value) == pytest.approx(mi_value * 1.61, rel=1e-3)

def test_calculate_distance(mocker):
    mocked_haversine = mocker.patch('find_store.haversine')
    find_store.calculate_distance((37.1, -122.2), (34.2, -122.4), 'km')
    mocked_haversine.assert_called_once_with(-122.2, 37.1, -122.4, 34.2, 'km')

def test_closest_store(mocker):
    with mocker.patch('find_store.sqlite3') as mocksql:
        mocksql.connect().cursor().execute.return_value = [
            ('A', 'A2', 'A3', 'A4', 'A5', 'A6', '77', '78', 'A9'),
            ('B', 'B2', 'B3', 'B4', 'B5', 'B6', '87', '88', 'B9'),
            ('C', 'C2', 'C3', 'C4', 'C5', 'C6', '97', '98', 'C9')
        ]
        mocked_calculate = mocker.patch('find_store.calculate_distance')
        mocked_calculate.return_value = 8
        answer = find_store.closest_store((37.1, -122.2), 'mi', mocksql.connect().cursor())
        assert mocked_calculate.call_count == 3
        assert answer == {
            'name': 'A',
            'location': 'A2',
            'address': 'A3',
            'city': 'A4',
            'state': 'A5',
            'zip': 'A6',
            'latitude': 77.0,
            'longitude': 78.0,
            'county': 'A9',
            'distance': 8,
            'units': 'mi',
        }

def test_format_output():
    mocked_store = {
        'name': 'A',
        'location': 'A2',
        'address': 'A3',
        'city': 'A4',
        'state': 'A5',
        'zip': 'A6',
        'latitude': 77.0,
        'longitude': 78.0,
        'county': 'A9',
        'distance': 8,
        'units': 'mi',
    }
    text = find_store.format_output(mocked_store, 'text')
    assert text == 'Your nearest store is 8.0 mi away in A. Please visit us at A3, A4, A5 A6.'
