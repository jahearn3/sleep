import datetime
import pandas as pd


def process_data(filename="sleep.csv"):
    df = pd.read_csv(filename)
    df['start_raw'] = df['start']
    df['stop_raw'] = df['stop']
    midnight = datetime.time()
    time_columns = ['start', 'stop']
    for ts in time_columns:
        if ts in df.columns:
            df[ts] = pd.to_datetime(df['date'] + ' ' + df[ts], errors='coerce')

    df['start'] = pd.to_datetime(df['start'])
    # add 12 hours to the start time
    df['start'] = df['start'] + datetime.timedelta(hours=12)
    # hours after midnight of the day prior
    df['start_time_hr'] = (
        (df['start'] - pd.to_datetime(df['date'] + ' ' + str(midnight)))
        .dt.total_seconds() / (60 * 60) - 24
    )
    # add one day to the stop time
    df['stop'] = pd.to_datetime(df['stop']) + datetime.timedelta(days=1)
    # hours after midnight of the day prior
    df['stop_time_hr'] = (
        (df['stop'] - pd.to_datetime(df['date'] + ' ' + str(midnight)))
        .dt.total_seconds()/(60*60) - 24
    )
    df['date'] = pd.to_datetime(df['date'])
    df['duration'] = (df['stop'] - df['start']).dt.total_seconds() / (60 * 60)
    return df
