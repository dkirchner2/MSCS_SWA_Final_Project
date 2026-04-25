from flask import Flask, request, render_template, jsonify
from datetime import datetime
import sys
import os
myDir = os.getcwd()
sys.path.append(myDir)
from collector.data_fetcher import initialize_data, get_location_data, fetch_daily_weather, get_city_weather_data
from analyzer.data_analyzer import get_monthly_weather_data


app = Flask(__name__)

@app.route("/")
def main():
    initialize_data()
    location_data = get_location_data()
    location_dict = [dict(row) for row in location_data] 
    return render_template('index.html', locations=location_dict)


@app.route("/yesterday", methods=["GET"])
def pull_yesterdays_weather():
    print('woo')
    initialize_data()
    yesterday_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    fetch_daily_weather(yesterday_date)


@app.route("/cities", methods=["POST"])
def get_city_weather():
    fetcher.initialize_data()
    data = request.get_json()
    city_data_results = []
    for city_idx in data.get('cities'):
        city_data_df = get_city_weather_data(city_idx)
        result = get_monthly_weather_data(city_data_df)
        city_data_results.append(result)
    return jsonify(city_data_results)

if __name__ == "__main__":
    app.run()