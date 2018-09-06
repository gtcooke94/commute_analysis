# -*- coding: utf-8 -*-
#import click import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import polyline

from stravalib.client import Client
import csv
import pdb
import os.path
import pandas as pd
import ast



#@click.command()
#@click.argument('input_filepath', type=click.Path(exists=True))
#@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    #logger = logging.getLogger(__name__)
    #logger.info('making final data set from raw data')


#if __name__ == '__main__':
    #log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    #project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    #load_dotenv(find_dotenv())

    #main()

def get_data():
    client = Client()
    load_dotenv(find_dotenv())
    authorize_url = client.authorization_url(client_id=os.getenv("client_id"),
            redirect_uri='http://localhost:8282/authorized')

    # Have the user click the authorization URL, a 'code' param will be added to the
    # redirect_uri
    # .....

    # Extract the code from your webapp response
    # code = request.get('code') # or whatever your framework does
    # access_token = client.exchange_code_for_token(client_id=22120,
    # client_secret='<client_secret>', code=code)

    client.access_token = os.getenv("access_token")
    activities = client.get_activities()
    types = ['time', 'latlng', 'altitude', 'heartrate', 'temp']
    headers_written = False
    #stream_types = ['time', 'latlng', 'altitude', 'heartrate', 'temp']
    stream_types = ['heartrate']
    with open(os.path.join("..", "data", "raw", 'raw_strava_data.csv'), 'w') as f:
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

def convert_data():
    ## Convert csv to h5 and store
    # h5 reference: https://realpython.com/fast-flexible-pandas/#selecting-data-with-isin

    strava_data = pd.read_csv(os.path.join('..', 'data', 'raw', 'raw_strava_data.csv'))
    drive_morning = pd.read_csv(os.path.join('..', 'data', 'raw', 'morning_commute.csv'))
    drive_evening = pd.read_csv(os.path.join('..', 'data', 'raw', 'evening_commute.csv'))
    # Convert time to usable things
    strava_data['elapsed_time'] = pd.to_timedelta(strava_data['elapsed_time'])

    strava_data['moving_time'] = pd.to_timedelta(strava_data['moving_time'])

    strava_data['start_date_local'] = pd.to_datetime(strava_data['start_date_local'])

    drive_evening['elapsed_time'] = pd.to_timedelta("00:" + drive_evening['Duration'])
    drive_morning['elapsed_time'] = pd.to_timedelta("00:" + drive_morning['Duration'])

    drive_morning['start_date_local'] = pd.to_datetime(drive_morning['Date'] + " " + drive_morning["Leave Time"], format="%Y-%m-%d %I:%M")
    drive_evening['start_date_local'] = pd.to_datetime(drive_evening['Date'] + " " + drive_evening["Leave Time"], format="%Y-%m-%d %I:%M:%S %p")


    # Convert defaults meters to miles
    strava_data['distance'] = strava_data['distance'] * 0.000621371

    # The map dictionary is a string coming from the csv
    strava_data["map"] = strava_data['map'].apply(ast.literal_eval)

    strava_data = add_start_end_latlng(strava_data)

    # Create storage object with filename `processed_data`
    data_store = pd.HDFStore(os.path.join('..', 'data', 'processed', 'strava_data.h5'))

    # Put DataFrame into the object setting the key as 'preprocessed_df'
    data_store['strava_data'] = strava_data
    data_store['drive_morning'] = drive_morning
    data_store['drive_evening'] = drive_evening
    data_store.close()
 

def load_data():
    # Access data store
    strava_data_h5 = pd.HDFStore(os.path.join('..', 'data', 'processed', 'strava_data.h5'))

    # Retrieve data using key
    strava_data = strava_data_h5['strava_data']
    drive_morning = strava_data_h5['drive_morning']
    drive_evening = strava_data_h5['drive_evening']
    strava_data_h5.close()
    return (strava_data, drive_morning, drive_evening)

def get_start_latlng(mp):
    pl = mp['summary_polyline']
    if pl:
        return(polyline.decode(pl)[0])

def get_end_latlng(mp):
    pl = mp['summary_polyline']
    if pl:
        return(polyline.decode(pl)[-1])

def add_start_end_latlng(strava_data):
    strava_data['start_latlng'] = strava_data['map'].apply(get_start_latlng)
    strava_data['end_latlng'] = strava_data['map'].apply(get_end_latlng)
    strava_data[['start_lat', 'start_lng']] = strava_data['start_latlng'].apply(pd.Series)
    strava_data[['end_lat', 'end_lng']] = strava_data['end_latlng'].apply(pd.Series)
    return strava_data
