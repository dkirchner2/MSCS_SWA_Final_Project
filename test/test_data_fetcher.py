import unittest
from unittest.mock import patch, MagicMock
from collector import data_fetcher
import sqlite3
import pandas as pd
import os
from datetime import datetime


class TestDataFetcher(unittest.TestCase):

    # -------------- COMMON TEST FUNCTIONS ------------------

    def setUp(self):
        # Create an in-memory database for testing
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        with open(os.path.join(self.BASE_DIR, '../collector/sql_migrations.sql')) as sql_file:
            sql_script = sql_file.read()
            self.cursor.executescript(sql_script)
            self.conn.commit()
        self.test_locations_df = pd.read_csv(os.path.join(self.BASE_DIR, 'test_data/test_locations.csv'))
        self.test_weather_1_df = pd.read_csv(os.path.join(self.BASE_DIR, 'test_data/test_weather_data/test_weather_1.csv'))
        self.test_weather_2_df = pd.read_csv(os.path.join(self.BASE_DIR, 'test_data/test_weather_data/test_weather_2.csv'))

    def tearDown(self):
        self.conn.close()

    # --------------- INITIALIZE_DATA() TESTS --------------------

    @patch('collector.data_fetcher.initialize_weather_data')
    @patch('collector.data_fetcher.initialize_locations')
    @patch('collector.data_fetcher.db.get_db_connection')
    @patch('collector.data_fetcher.db.initialize_db')
    def test_initialize_data_already_initialized(self, mock_init, mock_get_conn, mock_loc, mock_weather):
        mock_get_conn.return_value = (self.conn, self.cursor)
        mock_init.return_value = True

        data_fetcher.initialize_data()
        mock_get_conn.assert_not_called()
        mock_loc.assert_not_called()
        mock_weather.assert_not_called()


    @patch('collector.data_fetcher.initialize_weather_data')
    @patch('collector.data_fetcher.initialize_locations')
    @patch('collector.data_fetcher.db.get_db_connection')
    @patch('collector.data_fetcher.db.initialize_db')
    def test_initialize_data_not_already_initialized(self, mock_init, mock_get_conn, mock_loc, mock_weather):
        mock_get_conn.return_value = (self.conn, self.cursor)
        mock_init.return_value = False

        data_fetcher.initialize_data()
        mock_get_conn.assert_called_once()
        mock_loc.assert_called_once()
        mock_weather.assert_called_once()

    # -------------------- INITIALIZE_LOCATIONS() TESTS -------------------

    @patch('pandas.read_csv')
    def test_initialize_locations(self, mock_csv):
       mock_csv.return_value = self.test_locations_df
       data_fetcher.initialize_locations(self.conn)
       self.cursor.execute("SELECT cityName FROM Locations WHERE locationID=1")
       self.assertEqual(self.cursor.fetchone()[0], 'Los Angeles')


    @patch('pandas.read_csv')
    def test_initialize_locations_invalid_id(self, mock_csv):
        mock_csv.return_value = self.test_locations_df
        data_fetcher.initialize_locations(self.conn)
        self.cursor.execute("SELECT cityName FROM Locations WHERE locationID=3")
        self.assertEqual(self.cursor.fetchone(), None)
    
    # ---------------- INITIALIZE_WEATHER_DATA() TESTS ---------------------

    @patch('collector.data_fetcher.fetch_daily_weather')
    @patch('os.path.join')
    def test_initialize_weather_data_fills_db(self, mock_os, mock_daily):
        mock_os.return_value = self.BASE_DIR + '/test_data/test_weather_data'
        data_fetcher.initialize_weather_data(self.conn)
        # test test_weather_1.csv entry
        self.cursor.execute("SELECT maxTemp FROM WeatherEntries WHERE locationID=0 AND entryDate='2026-01-03'")
        self.assertEqual(self.cursor.fetchone()[0], 30.1)

        # test test_weather_2.csv entry
        self.cursor.execute("SELECT averageHumidity FROM WeatherEntries WHERE locationID=2 AND entryDate='2024-05-01'")
        self.assertEqual(self.cursor.fetchone()[0], 60)


    @patch('collector.data_fetcher.fetch_daily_weather')
    @patch('collector.data_fetcher.datetime',wraps=datetime)
    @patch('os.path.join')
    def test_initialize_weather_data_calls_api(self, mock_os, mock_datetime, mock_daily):
        mock_os.return_value = self.BASE_DIR + '/test_data/test_weather_data'
        fake_date = datetime.strptime('2026-04-25', '%Y-%m-%d')
        mock_datetime.now.return_value = fake_date
        data_fetcher.initialize_weather_data(self.conn)
        self.assertEqual(mock_daily.call_count, 8)

    # ------------ GET_LOCATION_DATA() TEST ---------------

    @patch('collector.data_fetcher.db.get_db_connection')
    @patch('pandas.read_csv')
    def test_get_location_data(self, mock_csv, mock_connection):
        mock_connection.return_value = (self.conn, self.cursor)
        mock_csv.return_value = self.test_locations_df
        data_fetcher.initialize_locations(self.conn)
        result = data_fetcher.get_location_data()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][1], 'New York City')

    # ------------ GET_CITY_WEATHER_DATA() TESTS -------------

    @patch('collector.data_fetcher.fetch_daily_weather')
    @patch('collector.data_fetcher.db.get_db_connection')
    @patch('os.path.join')
    def test_get_city_weather_data(self, mock_os, mock_connection, mock_daily):
        mock_os.return_value = self.BASE_DIR + '/test_data/test_weather_data'
        mock_connection.return_value = (self.conn, self.cursor)
        data_fetcher.initialize_weather_data(self.conn)
        result = data_fetcher.get_city_weather_data(2)
        self.assertEqual(result.shape[0], 18)
        for i in range(len(result)):
            self.assertEqual(result['locationID'][i], 2)

    @patch('collector.data_fetcher.fetch_daily_weather')
    @patch('collector.data_fetcher.db.get_db_connection')
    @patch('os.path.join')
    def test_get_city_weather_data_invalid_index(self, mock_os, mock_connection, mock_daily):
        mock_os.return_value = self.BASE_DIR + '/test_data/test_weather_data'
        mock_connection.return_value = (self.conn, self.cursor)
        data_fetcher.initialize_weather_data(self.conn)
        result = data_fetcher.get_city_weather_data(3)
        self.assertTrue(result.empty)

    # ----------------- FETCH_DAILY_WEATHER() TESTS ----------------

    @patch('requests.get')
    @patch('collector.data_fetcher.get_location_data')
    @patch('collector.data_fetcher.db.get_db_connection')
    @patch('pandas.read_csv')
    def test_fetch_daily_weather_request(self, mock_csv, mock_connection, mock_loc, mock_get):
        mock_csv.return_value = self.test_locations_df
        mock_connection.return_value = (self.conn, self.cursor)
        data_fetcher.initialize_locations(self.conn)
        mock_loc.return_value = self.cursor.execute('SELECT * FROM Locations').fetchall()
        expected_request = 'https://archive-api.open-meteo.com/v1/archive?latitude=40.42,34.03,41.52&longitude=-74.0,-118.15,-87.37&start_date=2026-04-24&end_date=2026-04-24&daily=temperature_2m_max,temperature_2m_min,daylight_duration,sunshine_duration,rain_sum,snowfall_sum,precipitation_hours,wind_gusts_10m_max,temperature_2m_mean,cloud_cover_mean,wind_speed_10m_mean,relative_humidity_2m_mean&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch'
        data_fetcher.fetch_daily_weather('2026-04-24')
        mock_get.assert_called_with(expected_request)

    
    @patch('requests.get')
    @patch('collector.data_fetcher.get_location_data')
    @patch('collector.data_fetcher.db.get_db_connection')
    @patch('pandas.read_csv')
    def test_fetch_daily_weather_data(self, mock_csv, mock_connection, mock_loc, mock_get):
        mock_csv.return_value = self.test_locations_df
        mock_connection.return_value = (self.conn, self.cursor)
        data_fetcher.initialize_locations(self.conn)
        mock_loc.return_value = self.cursor.execute('SELECT * FROM Locations').fetchall()

        test_response = [{'latitude': 34.059753, 'longitude': -118.125, 'generationtime_ms': 0.2454519271850586, 
        'utc_offset_seconds': 0, 'timezone': 'GMT', 'timezone_abbreviation': 'GMT', 'elevation': 73.0, 'location_id': 1, 
        'daily_units': {'time': 'iso8601', 'temperature_2m_max': '°F', 'temperature_2m_min': '°F', 'daylight_duration': 's', 
        'sunshine_duration': 's', 'rain_sum': 'inch', 'snowfall_sum': 'inch', 'precipitation_hours': 'h', 
        'wind_gusts_10m_max': 'mp/h', 'temperature_2m_mean': '°F', 'cloud_cover_mean': '%', 'wind_speed_10m_mean': 'mp/h', 
        'relative_humidity_2m_mean': '%'}, 'daily': {'time': ['2026-04-24'], 'temperature_2m_max': [75.5], 
        'temperature_2m_min': [56.8], 'daylight_duration': [48000.29], 'sunshine_duration': [45836.81], 'rain_sum': [0.0], 
        'snowfall_sum': [0.0], 'precipitation_hours': [0.0], 'wind_gusts_10m_max': [26.2], 'temperature_2m_mean': [65.9], 
        'cloud_cover_mean': [49], 'wind_speed_10m_mean': [4.4], 'relative_humidity_2m_mean': [54]}}, {'latitude': 41.51142, 
        'longitude': -87.40634, 'generationtime_ms': 0.21541118621826172, 'utc_offset_seconds': 0, 'timezone': 'GMT',
        'timezone_abbreviation': 'GMT', 'elevation': 215.0, 'location_id': 2, 'daily_units': {'time': 'iso8601',
        'temperature_2m_max': '°F', 'temperature_2m_min': '°F', 'daylight_duration': 's', 'sunshine_duration': 's',
        'rain_sum': 'inch', 'snowfall_sum': 'inch', 'precipitation_hours': 'h', 'wind_gusts_10m_max': 'mp/h',
        'temperature_2m_mean': '°F', 'cloud_cover_mean': '%', 'wind_speed_10m_mean': 'mp/h', 'relative_humidity_2m_mean': '%'},
        'daily': {'time': ['2026-04-24'], 'temperature_2m_max': [74.8], 'temperature_2m_min': [62.5], 
        'daylight_duration': [49404.85], 'sunshine_duration': [27480.27], 'rain_sum': [0.169], 'snowfall_sum': [0.0], 
        'precipitation_hours': [8.0], 'wind_gusts_10m_max': [28.2], 'temperature_2m_mean': [67.5], 'cloud_cover_mean': [93],
        'wind_speed_10m_mean': [9.1], 'relative_humidity_2m_mean': [69]}}, {'latitude': 32.442883, 'longitude': -96.451996,
        'generationtime_ms': 0.2130270004272461, 'utc_offset_seconds': 0, 'timezone': 'GMT', 'timezone_abbreviation': 'GMT',
        'elevation': 101.0, 'location_id': 3, 'daily_units': {'time': 'iso8601', 'temperature_2m_max': '°F', 
        'temperature_2m_min': '°F', 'daylight_duration': 's', 'sunshine_duration': 's', 'rain_sum': 'inch', 
        'snowfall_sum': 'inch', 'precipitation_hours': 'h', 'wind_gusts_10m_max': 'mp/h', 'temperature_2m_mean': '°F', 
        'cloud_cover_mean': '%', 'wind_speed_10m_mean': 'mp/h', 'relative_humidity_2m_mean': '%'},
        'daily': {'time': ['2026-04-24'], 'temperature_2m_max': [87.0], 'temperature_2m_min': [69.7], 
        'daylight_duration': [47731.82], 'sunshine_duration': [32832.23], 'rain_sum': [0.012], 'snowfall_sum': [0.0], 
        'precipitation_hours': [2.0], 'wind_gusts_10m_max': [30.2], 'temperature_2m_mean': [77.1], 'cloud_cover_mean': [75],
        'wind_speed_10m_mean': [14.5], 'relative_humidity_2m_mean': [72]}}] 

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_response
        mock_get.return_value = mock_response

        data_fetcher.fetch_daily_weather('2026-04-24')

        result = self.cursor.execute('SELECT * FROM WeatherEntries').fetchall()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][1], 0)
        self.assertEqual(result[1][3], 74.8)
        self.assertEqual(result[2][12], 75)

    @patch('requests.get')
    @patch('collector.data_fetcher.get_location_data')
    @patch('collector.data_fetcher.db.get_db_connection')
    @patch('pandas.read_csv')
    def test_fetch_daily_weather_no_data(self, mock_csv, mock_connection, mock_loc, mock_get):
        mock_csv.return_value = self.test_locations_df
        mock_connection.return_value = (self.conn, self.cursor)
        data_fetcher.initialize_locations(self.conn)
        mock_loc.return_value = self.cursor.execute('SELECT * FROM Locations').fetchall()

        test_response = {
            "error": True, 
            "reason": "Cannot initialize WeatherVariable from invalid String value tempeture_2m for key hourly" 
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = test_response
        mock_get.return_value = mock_response

        data_fetcher.fetch_daily_weather('2026-04-24')
        result = self.cursor.execute('SELECT * FROM WeatherEntries').fetchall()
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)