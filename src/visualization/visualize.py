import pandas as pd
import folium
import polyline

def prepare_for_plotting(df):
    to_plot = df.copy()
    if 'moving_time' in to_plot.columns:
        to_plot["moving_time"] = to_plot["moving_time"].apply(pd.to_timedelta)
        to_plot['moving_time'] = to_plot.loc[:, 'moving_time'] / pd.Timedelta(minutes=1)
    to_plot['elapsed_time'] = to_plot.loc[:, 'elapsed_time'] / pd.Timedelta(minutes=1)
    return to_plot


def plot_polylines(df, map_lat_lng):
    m = folium.Map(map_lat_lng, zoom_start=14)
    for (index, row) in df.iterrows():
        if (row['map']['summary_polyline']):
            pl = polyline.decode(row['map']['summary_polyline'])
            bike_path = folium.PolyLine(pl).add_to(m)
    return m
