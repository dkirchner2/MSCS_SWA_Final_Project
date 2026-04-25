from flask import Flask, request, render_template, jsonify
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'collector')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'analyzer')))
import collector.data_fetcher as fetcher
import analyzer.data_analyzer as analyzer


app = Flask(__name__)

@app.route("/")
def main():
    fetcher.initialize_data()
    location_data = fetcher.get_location_data()
    location_dict = [dict(row) for row in location_data] 
    return render_template('index.html', locations=location_dict)


@app.route("/yesterday", methods=["GET"])
def pull_yesterdays_weather():
    print('woo')
    fetcher.initialize_data()
    yesterday_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    fetcher.fetch_daily_weather(yesterday_date)


@app.route("/cities", methods=["POST"])
def get_city_weather():
    fetcher.initialize_data()
    data = request.get_json()
    city_data_results = []
    for city_idx in data.get('cities'):
        city_data_df = fetcher.get_city_weather_data(city_idx)
        print(city_data_df)
        result = analyzer.get_monthly_weather_data(city_data_df)
        city_data_results.append(result)
    return jsonify(city_data_results)

