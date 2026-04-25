import pandas as pd

def get_monthly_weather_data(raw_city_data_df):
    
    raw_city_data_df['daylightDuration'] = raw_city_data_df['daylightDuration'] / 3600
    raw_city_data_df['sunlightDuration'] = raw_city_data_df['sunlightDuration'] / 3600
    raw_city_data_df['year'] = raw_city_data_df['entryDate'].str[:4]
    raw_city_data_df['month'] = raw_city_data_df['entryDate'].str[5:7]
    
    # total_monthly_rain = raw_city_data_df['rainInches', 'snowInches].groupby(['month', 'year']).sum(numeric_only=True)
    # avg_monthly_rain = total_monthly_rain.groupby(['year']).mean().apply(lambda x: x.to_dict()).to_dict()
    # result_dict['rainInches'] = avg_monthly_rain['rainInches']

    combined_month_data_mean = raw_city_data_df.groupby(['month']).mean(numeric_only=True).apply(lambda x: x.to_dict()).to_dict()
    combined_month_data_max = raw_city_data_df.groupby(['month']).max(numeric_only=True).apply(lambda x: x.to_dict()).to_dict()
    combined_month_data_min = raw_city_data_df.groupby(['month']).min(numeric_only=True).apply(lambda x: x.to_dict()).to_dict()
    result_dict = {
        'combined_monthly_means': combined_month_data_mean,
        'combined_monthly_maxes': combined_month_data_max,
        'combined_monthly_mins': combined_month_data_min
    }

    total_monthly_rain = raw_city_data_df.groupby(['month', 'year']).sum(numeric_only=True)
    avg_monthly_rain = total_monthly_rain.groupby(['month']).mean().apply(lambda x: x.to_dict()).to_dict()
    max_monthly_rain = total_monthly_rain.groupby(['month']).max().apply(lambda x: x.to_dict()).to_dict()
    min_monthly_rain = total_monthly_rain.groupby(['month']).min().apply(lambda x: x.to_dict()).to_dict()
    result_dict['combined_monthly_means']['rainInchesMonthly'] = avg_monthly_rain['rainInches']
    result_dict['combined_monthly_means']['snowInchesMonthly'] = avg_monthly_rain['snowInches']
    result_dict['combined_monthly_maxes']['rainInchesMonthly'] = max_monthly_rain['rainInches']
    result_dict['combined_monthly_maxes']['snowInchesMonthly'] = max_monthly_rain['snowInches']
    result_dict['combined_monthly_mins']['rainInchesMonthly'] = min_monthly_rain['rainInches']
    result_dict['combined_monthly_mins']['snowInchesMonthly'] = min_monthly_rain['snowInches']
    return result_dict
