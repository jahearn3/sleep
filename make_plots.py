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

    # plot duration vs date
    fig = plt.figure()
    plt.plot(df['date'], df['duration'], color='black')
    plt.scatter(df['date'], df['duration'], color='black')
    plt.xlabel('Date')
    plt.ylabel('Sleep Duration')
    plt.title('Sleep Duration Over Time')
    # Add horizontal lines at certain hours
    y_min, y_max = plt.ylim()
    plt.axhspan(7.5, y_max, facecolor='lightgreen', alpha=0.5)
    plt.axhspan(6.5, 7.5, facecolor='khaki', alpha=0.5)
    plt.axhspan(y_min, 6.5, facecolor='lightcoral', alpha=0.5)
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
    bin_interval = 0.25
    fig = plt.figure()
    bin_min = math.floor(min(df['duration']) / bin_interval) * bin_interval
    bin_max = math.ceil(max(df['duration']) / bin_interval) * bin_interval
    bin_edges = np.arange(bin_min, bin_max + bin_interval, bin_interval)
    # cmap = plt.cm.get_cmap('RdYlGn')
    # n, bins, patches = plt.hist(df['duration'], bins=bin_edges)
    # for patch, bin_val in zip(patches, bins):
    #     color_val = (bin_val - min(bins)) / (max(bins) - min(bins))
        # patch.set_facecolor(cmap(color_val))
    counts, _ = np.histogram(df['duration'], bins=bin_edges)
    colors = []
    for i in range(len(bin_edges) - 1):
        if bin_edges[i+1] <= 6.5:
            colors.append('red')
        elif bin_edges[i] >= 7.5:
            colors.append('green')
        else:
            colors.append('yellow')
    plt.bar(bin_edges[:-1], counts, width=np.diff(bin_edges), color=colors, edgecolor='black')
    # plt.axvline(separation_point, color='black', linestyle='--')
    plt.xlabel('Sleep Duration')
    plt.ylabel('Frequency')
    plt.title('Sleep Duration Histogram')
    plt.savefig('sleep_duration_histogram.png',  bbox_inches='tight')
    plt.clf()

    # plot lines for each day
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for index, row in df.iterrows():
        date = row['date']
        start_time = row['start_time_hr']
        stop_time = row['stop_time_hr']
        c = 'k'
        if row['duration'] < 6.5:
            c = 'r'
        elif row['duration'] < 7.5:
            c = 'y'
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