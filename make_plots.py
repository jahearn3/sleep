import datetime
import math
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def plot_sleep(filename="sleep.csv"):
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
    df['start_time_hr'] = (df['start'] - pd.to_datetime(df['date'] + ' ' + str(midnight))).dt.total_seconds()/(60*60) - 24
    # add one day to the stop time
    df['stop'] = pd.to_datetime(df['stop']) + datetime.timedelta(days=1)
    # hours after midnight of the day prior
    df['stop_time_hr'] = (df['stop'] - pd.to_datetime(df['date'] + ' ' + str(midnight))).dt.total_seconds()/(60*60) - 24
    df['date'] = pd.to_datetime(df['date'])
    df['duration'] = (df['stop'] - df['start']).dt.total_seconds() / (60 * 60)

    # df['duration2'] = (df['stop_time_hr'] - df['start_time_hr']).dt.total_seconds() / (60 * 60)
    # print(df[['duration', 'start_time_hr', 'start', 'stop_time_hr', 'stop']])
    # midnight = datetime.time()
    # df['start'] = (df['start'] - pd.to_datetime(df['date'] + ' ' + str(midnight))).dt.total_seconds() / (60 * 60)
    # df['stop'] = (df['stop'] - pd.to_datetime(df['date'] + ' ' + str(midnight))).dt.total_seconds() / (60 * 60)
    # print(df.head())

    # formatted_dates = df['date'].dt.strftime('%Y-%m-%d')
    # print(formatted_dates)
    # df['date_num'] = df['date'].apply(date2num)

    # plot duration vs date
    fig = plt.figure()
    # lm = sns.lmplot(data=df, x='date_num', y='duration', ci=None)
    # plt.plot(df['date_num'], df['duration'], color='black')
    plt.plot(df['date'], df['duration'], color='black')
    plt.scatter(df['date'], df['duration'], color='black')
    # ax = lm.ax
    plt.xlabel('Date')
    plt.ylabel('Sleep Duration')
    plt.title('Sleep Duration Over Time')
    # Add horizontal lines at certain hours
    y_min, y_max = plt.ylim()
    plt.axhspan(8, y_max, facecolor='lightgreen', alpha=0.5)
    plt.axhspan(7, 8, facecolor='lightcyan', alpha=0.5)
    plt.axhspan(6, 7, facecolor='khaki', alpha=0.5)
    plt.axhspan(y_min, 6, facecolor='lightcoral', alpha=0.5)
    plt.ylim(y_min, y_max)
    # Set the tick locator to ensure proper spacing with a custom interval
    tick_interval = int(len(df['date']) / 7) + 1
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=tick_interval))
    # Set the tick formatter to display your desired date format
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # Rotate the tick labels for better readability
    plt.xticks(rotation=90)
    plt.savefig('sleep_duration_over_time.png',  bbox_inches='tight')
    plt.clf()

    # histogram of duration in intervals of 0.25
    bin_interval = 0.5
    fig = plt.figure()
    bin_min = math.floor(min(df['duration']) / bin_interval) * bin_interval # math.floor(df['duration'].min())
    bin_max = math.ceil(max(df['duration']) / bin_interval) * bin_interval # math.ceil(df['duration'].max())
    bin_edges = np.arange(bin_min, bin_max + bin_interval, bin_interval) 
    cmap = plt.cm.get_cmap('RdYlGn')
    n, bins, patches = plt.hist(df['duration'], bins=bin_edges)
    for patch, bin_val in zip(patches, bins):
        color_val = (bin_val - min(bins)) / (max(bins) - min(bins))
        patch.set_facecolor(cmap(color_val))
    plt.xlabel('Sleep Duration')
    plt.ylabel('Frequency')
    plt.title('Sleep Duration Histogram')
    plt.savefig('sleep_duration_histogram.png',  bbox_inches='tight')
    plt.clf()

    # plot lines for each day
    # Create a new column for the combined date and time
    # print(df[['start', 'stop']].head(10))
    # new_start_date = '2024-09-03'
    # new_end_date = '2024-09-04'
    # # Create a new column that combines the date 2024-09-03 with the time for each row
    # df['start_time'] = df['start_raw'].str.replace(r'\d{4}-\d{2}-\d{2}', new_start_date, regex=True)
    # df['start_time'] = pd.to_datetime(df['start_time']) + datetime.timedelta(hours=12)
    # df['end_time'] = df['stop_raw'].str.replace(r'\d{4}-\d{2}-\d{2}', new_end_date, regex=True)
    # df['end_time'] = pd.to_datetime(df['end_time'])
    # df['start_t'] = df.apply(lambda row: row['date'] + pd.DateOffset(hours=row['start'].hour, minutes=row['start'].minute, seconds=row['start'].second), axis=1)
    # print(df[['date', 'start_time', 'end_time']].head(15))
    # df['start_datetime'] = df.apply(lambda row: row['date'].replace(hour=row['start'].hour, minute=row['start'].minute, second=row['start'].second), axis=1)
    # df['stop_datetime'] = df.apply(lambda row: (row['date'] + pd.DateOffset(days=1)).replace(hour=row['stop'].hour, minute=row['stop'].minute, second=row['stop'].second), axis=1)
    # fig, ax = plt.subplots()
    # for index, row in df.iterrows():
    #     start_time = row['start_time'].strftime('%H:%M')
    #     stop_time = row['end_time'].strftime('%H:%M')
    #     ax.plot([row['date'], row['date']], [start_time, stop_time], 'k-')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    first_sunset = 7.75 - 12  # 7:45 am on 2024-09-03
    first_sunrise = 6.57      # 6:34 am on 2024-09-04
    last_sunset = 6.77 - 12   # 6:46 am on 2024-10-02
    last_sunrise = 7.22       # 7:13 am on 2024-10-03
    first_date = df['date'].min()
    last_date = df['date'].max()
    # ax.plot([first_sunset, last_sunset],[first_date, last_date], color='lightgrey', alpha=0.5)
    # ax.plot([first_sunrise, last_sunrise],[first_date, last_date], color='lightgrey', alpha=0.5)
    for index, row in df.iterrows():
        date = row['date']
        start_time = row['start_time_hr']  #.strftime('%H:%M')
        stop_time = row['stop_time_hr']  #.strftime('%H:%M')
        c = 'k' 
        if row['duration'] < 6.5:
            c = 'r' 
        # elif row['duration'] < 6.5:
        #     c = 'darkorange'
        elif row['duration'] < 7.5:
            c = 'y'
        # elif row['duration'] < 7.5:
        #     c = 'y'
        # elif row['duration'] < 8:
        #     c = 'lightgreen'
        else: 
            c = 'g'
        ax.plot([start_time, stop_time], [date, date], color=c)

    tick_labels = {
        -4: '8:00',
        -3: '9:00',
        -2: '10:00',
        -1: '11:00',
        0: '12:00',
        1: '1:00',
        2: '2:00',
        3: '3:00',
        4: '4:00',
        5: '5:00',
        6: '6:00',
        7: '7:00',
        8: '8:00',
        9: '9:00',
        10: '10:00',
    }
    plt.xticks(ticks=list(tick_labels.keys()), labels=list(tick_labels.values()))
    ax.set_xlim(df['start_time_hr'].min() - 0.5, df['stop_time_hr'].max() + 0.5)

    plt.xlabel('Time')
    plt.ylabel('Date')
    plt.title('Sleep Sessions')
    plt.savefig('sleep_times_each_day.png',  bbox_inches='tight')
    plt.clf()

    # Violin plot of sleep duration with day of week as hue
    fig = plt.figure()
    ax = sns.violinplot(data=df, x='duration', y='day_of_week', order=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])
    plt.xlabel('Sleep Duration')
    plt.ylabel('Day of Week')
    plt.title('Sleep Duration by Day of Week')
    plt.savefig('sleep_duration_by_day_of_week.png',  bbox_inches='tight')
    plt.clf()


plot_sleep()