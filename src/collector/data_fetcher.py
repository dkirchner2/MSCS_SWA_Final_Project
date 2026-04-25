import collector.db_handler as db
import pandas as pd
from datetime import datetime, timedelta
import requests
from collector.fields_dict import fields_dict
from pathlib import Path
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'weather_data.db')
BASE_URL = 'https://archive-api.open-meteo.com/v1/archive?'
LAST_HISTORICAL_DATA_DATE = '2026-04-17'

def initialize_data():
    already_initialized = db.initialize_db(DB_NAME)
    if not already_initialized:
        conn, cursor = db.get_db_connection(DB_NAME)
        initialize_locations(conn)
        initialize_weather_data(conn)
        conn.close()


def initialize_locations(conn):
    location_df = pd.read_csv(os.path.join(BASE_DIR, 'locations.csv'))
    location_df['created'] = datetime.now()
    location_df.to_sql('Locations', con=conn, if_exists='replace', index=False)
    conn.commit()


def initialize_weather_data(conn):
    first_file = True
    data_folder_path = os.path.join(BASE_DIR, 'historical_weather_data')
    for file in Path(data_folder_path).iterdir():
        if file.is_file() and "DS_Store" not in file.name:
            print(file, flush=True)
            weather_df = pd.read_csv(f'{data_folder_path}/{file.name}', encoding = "utf-8")
            weather_df['created'] = datetime.now()
            if first_file:
                weather_df.to_sql('WeatherEntries', conn, if_exists='replace', index=False)
                first_file = False
            else:
                weather_df.to_sql('WeatherEntries', conn, if_exists='append', index=False)

    time_delta = timedelta(1)
    curr_date = datetime.strptime(LAST_HISTORICAL_DATA_DATE, '%Y-%m-%d')
    while curr_date <= datetime.now() - time_delta:
        date_string = datetime.strftime(curr_date, '%Y-%m-%d')
        fetch_daily_weather(date_string)
        curr_date += time_delta


def get_location_data():
    conn, cursor = db.get_db_connection(DB_NAME)
    results = cursor.execute('SELECT * FROM Locations').fetchall()
    conn.close()
    return results


def get_city_weather_data(city_index):
    conn, cursor = db.get_db_connection(DB_NAME)
    query = f'SELECT * FROM WeatherEntries WHERE locationID = {city_index}'
    data_df = pd.read_sql_query(query, conn)
    return data_df


def fetch_daily_weather(date_string):
    conn, cursor = db.get_db_connection(DB_NAME)
    cities = get_location_data()
    latitudes = ','.join([i[3] for i in cities])
    longitudes = ','.join([str(i[4]) for i in cities])
    fields = ','.join(list(fields_dict))
    query = BASE_URL + "latitude=" + latitudes + "&longitude=" + longitudes \
    + "&start_date=" + date_string + "&end_date=" + date_string \
    + "&daily=" + fields + "&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"

    data = {}
    response = requests.get(query)
    if response.status_code == 200:
        data = response.json()

    if not data:
        print("error: no data")
    else:
        for i, location in enumerate(data):
            column_query_string = ', '.join([i[1] for i in sorted(fields_dict.items())])
            del location['daily']['time']
            value_query_data = [i[1][0] for i in sorted(location['daily'].items())]

            cityId = cursor.execute('''SELECT locationID FROM Locations WHERE cityName = ?''', (cities[i],)).fetchone()

            weather_insert_query = 'INSERT INTO WeatherEntries (' + column_query_string + ', locationID, entryDate, created) VALUES (' \
                + ', '.join(['?' for i in range(len(fields_dict.items()) + 3)]) + ')'
            cursor.execute(weather_insert_query, tuple(value_query_data + [cityId[0], date_string, datetime.now()]))
            conn.commit()
    conn.close()
