def split_morning_evening(strava_data):
    morning_mask = strava_data['start_date_local'].dt.hour.isin(range(7, 11))
    evening_mask = strava_data['start_date_local'].dt.hour.isin(range(14, 20))
    weekday_mask = strava_data['start_date_local'].dt.weekday.isin(range(0, 5))
    normal_time_mask = ((strava_data['moving_time'].dt.seconds / 60) > 10) & ((strava_data['moving_time'].dt.seconds / 60) < 30)
    bike_mask = strava_data['type'] == 'Ride'
    distance_mask = (strava_data['distance'] > 2.8) & (strava_data['distance'] < 4.7)
    gtri_start_mask = strava_data['start_lat'] >= 33.781
    gt_start_mask = (strava_data['start_lat'] <= 33.781) & (strava_data['start_lng'] <= -84.38)
    gtri_end_mask = strava_data['end_lat'] >= 33.781
    gt_end_mask = (strava_data['end_lat'] <= 33.781) & (strava_data['start_lng'] <= -84.38)

    morning_commutes = strava_data[morning_mask & weekday_mask & normal_time_mask & distance_mask & (gtri_end_mask | gt_end_mask)]
    evening_commutes = strava_data[evening_mask & weekday_mask & normal_time_mask & distance_mask & (gtri_start_mask | gt_end_mask)]
    return (morning_commutes, evening_commutes)
