from stravalib.client import Client
from strava_keys import client_id, client_secret, access_token
import csv
import pdb
import os.path
import pandas as pd

client = Client()
authorize_url = client.authorization_url(client_id=client_id,
		redirect_uri='http://localhost:8282/authorized')
# Have the user click the authorization URL, a 'code' param will be added to the
# redirect_uri
# .....

# Extract the code from your webapp response
# code = request.get('code') # or whatever your framework does
# access_token = client.exchange_code_for_token(client_id=22120,
# client_secret='<client_secret>', code=code)

client.access_token = access_token


if (os.path.isfile('raw_strava_data--------------.csv')):
	strava_data = pd.read_csv('raw_strava_data.csv')
	strava_data['start_date_local'] = pd.to_datetime(strava_data['start_date_local'])
	activities = client.get_activities(strava_data['start_date_local'].max())
	for activity in activities:
		strava_data.append(pd.from_dict(activity.to_dict()), ignore_index=True)
	stava_data.to_csv('raw_strava_data.csv')
else:
	activities = client.get_activities()
	types = ['time', 'latlng', 'altitude', 'heartrate', 'temp']
	headers_written = False
	#stream_types = ['time', 'latlng', 'altitude', 'heartrate', 'temp']
	stream_types = ['heartrate']
	with open('raw_strava_data.csv', 'w') as f:
		for activity in activities:
			streams = client.get_activity_streams(activity.id, types=stream_types, resolution='medium')
			temp = activity.to_dict()
			for k in types:
				if k in streams:
					temp[k] = streams[k].data
				else:
					temp[k] = None
			if not headers_written:
				w = csv.DictWriter(f, temp.keys())
				w.writeheader()
				headers_written = True
			w.writerow(temp)

# Get datetime from string. This is for later for updating the data
# t = datetime.strptime(str, '%Y-%m-%dT%H:%M:%S')
