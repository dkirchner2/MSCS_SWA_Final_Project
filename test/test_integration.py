from collector.data_fetcher import initialize_locations, initialize_weather_data, get_city_weather_data
from analyzer.data_analyzer import get_monthly_weather_data
from collector.db_handler import initialize_db, get_db_connection
import os

# test the functionality of the /cities endpoint
def test_city_weather_functionality():
    city_index_arr = [0, 1, 2]

    conn, cursor = get_db_connection(":memory:")
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'collector/sql_migrations.sql')) as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)
            conn.commit()
    locations_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data/test_locations.csv')
    weather_data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data/test_weather_data')
    initialize_locations(conn, datafile=locations_file)
    initialize_weather_data(conn, datafolder=weather_data_folder)

    city_data_results = []
    for city_idx in city_index_arr:
        city_data_df = get_city_weather_data(city_idx, conn=conn, cursor=cursor)
        result = get_monthly_weather_data(city_data_df)
        city_data_results.append(result)
    assert(len(city_data_results) == 3)
    assert('combined_monthly_means' in city_data_results[0])
    assert(city_data_results[1]['combined_monthly_maxes']['minTemp']['09'] == 71.2)
    assert(city_data_results[2]['combined_monthly_mins']['snowInchesMonthly']['01'] == 0.221)

