# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

from stravalib.client import Client
import csv
import pdb
import os.path
import pandas as pd



@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()

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

def load_data():
    # Access data store
    strava_data_h5 = pd.HDFStore(os.path.join('..', 'data', 'processed', 'strava_data.h5'))

    # Retrieve data using key
    strava_data = strava_data_h5['strava_data']
    drive_morning = strava_data_h5['drive_morning']
    drive_evening = strava_data_h5['drive_evening']
    strava_data_h5.close()
    return (strava_data, drive_morning, drive_evening)

