import unittest
from unittest.mock import patch, MagicMock
from collector import data_fetcher
from analyzer import data_analyzer
import sqlite3
import pandas as pd
import os
from datetime import datetime


class TestDataAnalyzer(unittest.TestCase):

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

    # -------------- GET_MONTHLY_WEATHER_DATA() TESTS ---------------

    @patch('collector.data_fetcher.fetch_daily_weather')
    @patch('os.path.join')
    def test_get_monthly_weather_data_basic_cleaning(self, mock_os, mock_daily):
        mock_os.return_value = self.BASE_DIR + '/test_data/test_weather_data'
        data_fetcher.initialize_weather_data(self.conn)
        data_df = pd.read_sql_query('SELECT * FROM WeatherEntries', self.conn)

        result = data_analyzer.get_monthly_weather_data(data_df[data_df['locationID'] == 2])
        self.assertLess(result['combined_monthly_means']['daylightDuration']['01'], 24)
        self.assertLess(result['combined_monthly_means']['sunlightDuration']['09'], 24)
        self.assertLess(result['combined_monthly_maxes']['daylightDuration']['01'], 24)
        self.assertLess(result['combined_monthly_maxes']['sunlightDuration']['09'], 24)
        self.assertLess(result['combined_monthly_mins']['daylightDuration']['01'], 24)
        self.assertLess(result['combined_monthly_mins']['sunlightDuration']['09'], 24)

    
    @patch('collector.data_fetcher.fetch_daily_weather')
    @patch('os.path.join')
    def test_get_monthly_weather_max_temp(self, mock_os, mock_daily):
        mock_os.return_value = self.BASE_DIR + '/test_data/test_weather_data'
        data_fetcher.initialize_weather_data(self.conn)
        data_df = pd.read_sql_query('SELECT * FROM WeatherEntries', self.conn)

        result = data_analyzer.get_monthly_weather_data(data_df[data_df['locationID'] == 0])
        self.assertAlmostEqual(result['combined_monthly_means']['maxTemp']['01'], 37.97, delta=0.1)
        self.assertAlmostEqual(result['combined_monthly_maxes']['maxTemp']['01'], 50.9, delta=0.1)
        self.assertAlmostEqual(result['combined_monthly_mins']['maxTemp']['01'], 30.1, delta=0.1)
        

    @patch('collector.data_fetcher.fetch_daily_weather')
    @patch('os.path.join')
    def test_get_monthly_weather_min_temp(self, mock_os, mock_daily):
        mock_os.return_value = self.BASE_DIR + '/test_data/test_weather_data'
        data_fetcher.initialize_weather_data(self.conn)
        data_df = pd.read_sql_query('SELECT * FROM WeatherEntries', self.conn)

        result = data_analyzer.get_monthly_weather_data(data_df[data_df['locationID'] == 1])
        self.assertAlmostEqual(result['combined_monthly_means']['minTemp']['09'], 67.2, delta=0.1)
        self.assertAlmostEqual(result['combined_monthly_maxes']['minTemp']['09'], 71.2, delta=0.1)
        self.assertAlmostEqual(result['combined_monthly_mins']['minTemp']['09'], 63.5, delta=0.1)


    @patch('collector.data_fetcher.fetch_daily_weather')
    @patch('os.path.join')
    def test_get_monthly_weather_rain_monthly(self, mock_os, mock_daily):
        mock_os.return_value = self.BASE_DIR + '/test_data/test_weather_data'
        data_fetcher.initialize_weather_data(self.conn)
        data_df = pd.read_sql_query('SELECT * FROM WeatherEntries', self.conn)

        result = data_analyzer.get_monthly_weather_data(data_df[data_df['locationID'] == 0])
        self.assertAlmostEqual(result['combined_monthly_means']['rainInchesMonthly']['05'], 0.2, delta=0.01)
        self.assertAlmostEqual(result['combined_monthly_maxes']['rainInchesMonthly']['05'], 0.274, delta=0.01)
        self.assertAlmostEqual(result['combined_monthly_mins']['rainInchesMonthly']['05'], 0.126, delta=0.01)


    @patch('collector.data_fetcher.fetch_daily_weather')
    @patch('os.path.join')
    def test_get_monthly_weather_snow_monthly(self, mock_os, mock_daily):
        mock_os.return_value = self.BASE_DIR + '/test_data/test_weather_data'
        data_fetcher.initialize_weather_data(self.conn)
        data_df = pd.read_sql_query('SELECT * FROM WeatherEntries', self.conn)

        result = data_analyzer.get_monthly_weather_data(data_df[data_df['locationID'] == 2])
        self.assertAlmostEqual(result['combined_monthly_means']['snowInchesMonthly']['01'], 0.262, delta=0.01)
        self.assertAlmostEqual(result['combined_monthly_maxes']['snowInchesMonthly']['01'], 0.303, delta=0.01)
        self.assertAlmostEqual(result['combined_monthly_mins']['snowInchesMonthly']['01'], 0.221, delta=0.01)


if __name__ == "__main__":
    unittest.main(verbosity=2)