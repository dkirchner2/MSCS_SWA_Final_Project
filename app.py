from flask import Flask, request, render_template, jsonify
from datetime import datetime, timedelta
from collector.data_fetcher import initialize_data, get_location_data, fetch_daily_weather, get_city_weather_data
from analyzer.data_analyzer import get_monthly_weather_data
from prometheus_client import Counter, generate_latest


app = Flask(__name__)
total_requests_metric = Counter('total_requests', 'Calls to all non-metrics endpoints')
city_search_metric = Counter('city_search', 'Calls to /cities endpoint')
city_count_metric = Counter('city_count', 'Number of cities called in /cities endpoint')


@app.route("/")
def main():
    total_requests_metric.inc()
    initialize_data()
    location_data = get_location_data()
    location_dict = [dict(row) for row in location_data] 
    return render_template('index.html', locations=location_dict)


@app.route("/yesterday", methods=["POST"])
def pull_yesterdays_weather():
    total_requests_metric.inc()
    initialize_data()
    yesterday_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    fetch_daily_weather(yesterday_date)
    return "Success!"


@app.route("/cities", methods=["POST"])
def get_city_weather():
    total_requests_metric.inc()
    city_search_metric.inc()
    initialize_data()
    data = request.get_json()
    city_data_results = []
    for city_idx in data.get('cities'):
        city_count_metric.inc()
        city_data_df = get_city_weather_data(city_idx)
        result = get_monthly_weather_data(city_data_df)
        city_data_results.append(result)
    return jsonify(city_data_results)


@app.route("/health", methods=['GET'])
def get_app_health():
    return jsonify({"status": "healthy"}), 200


@app.route("/metrics", methods=['GET'])
def get_metrics():
    return generate_latest(), 200


if __name__ == "__main__":
    app.run()