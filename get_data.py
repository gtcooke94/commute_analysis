from stravalib.client import Client
from strava_keys import client_id, client_secret, access_token
import csv
import pdb

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
activities = client.get_activities()
with open('strava_data.csv', 'w') as f:
    headers_written = False 
    for activity in activities:
        temp = activity.to_dict()
        if not headers_written:
            w = csv.DictWriter(f, temp.keys())
            headers_written = True
        w.writeheader()
        w.writerow(temp)

# Get datetime from string. This is for later for updating the data
# t = datetime.strptime(str, '%Y-%m-%dT%H:%M:%S')
