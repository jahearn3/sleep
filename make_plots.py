import datetime
import math
import matplotlib.dates as mdates
import matplotlib.patches as patches
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
    plt.bar(bin_edges[:-1], counts, width=np.diff(bin_edges), color=colors, edgecolor='black', alpha=0.5)
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

    # Plot comparing calculated duration to duration reported by smartwatch

    # Drop null values
    df_notna = df.dropna(subset=['duration_smartwatch'])

    # Convert duration_smartwatch to float
    df_notna.loc[:, 'duration_smartwatch'] = df_notna['duration_smartwatch'].apply(
        lambda x: (int(x.split(':')[0]) + int(x.split(':')[1]) / 60.0) if isinstance(x, str) else 0
    )

    fig, ax = plt.subplots()

    # Background colors
    background_yellow_rect = patches.Rectangle((5,5), 4, 4, color='khaki', zorder=1)
    ax.add_patch(background_yellow_rect)

    green_vertices = [[9,9], [6,9], [9,6]]
    green_triangle = patches.Polygon(green_vertices, closed=True, color='lightgreen', zorder=2)
    ax.add_patch(green_triangle)

    red_vertices = [[5,5], [8,5], [5,8]]
    red_triangle = patches.Polygon(red_vertices, closed=True, color='lightcoral', zorder=2)
    ax.add_patch(red_triangle)

    plt.scatter(df_notna['duration'], df_notna['duration_smartwatch'], zorder=5)
    plt.xlabel('Calculated Duration')
    plt.ylabel('Smartwatch Duration')
    ax.set_xlim(5, 9)
    ax.set_ylim(5, 9)
    tick_labels = {
        5: '5:00',
        6: '6:00',
        7: '7:00',
        8: '8:00',
        9: '9:00',
    }
    plt.xticks(ticks=list(tick_labels.keys()), labels=list(tick_labels.values()))
    plt.yticks(ticks=list(tick_labels.keys()), labels=list(tick_labels.values()))
    min_key = min(tick_labels.keys())
    max_key = max(tick_labels.keys())
    # Dotted lines
    ax.plot([min_key, max_key], [min_key, max_key], color='blue', linestyle='--', zorder=4)
    ax.plot([min_key + 1, max_key], [min_key, max_key - 1], color='gray', linestyle='--', zorder=4)
    ax.plot([min_key + 2, max_key], [min_key, max_key - 2], color='gray', linestyle='--', zorder=4)
    ax.axhline(y=6.5, color='gray', linestyle=':', linewidth=1, zorder=3)
    ax.axvline(x=6.5, color='gray', linestyle=':', linewidth=1, zorder=3)
    ax.axhline(y=7.5, color='gray', linestyle=':', linewidth=1, zorder=3)
    ax.axvline(x=7.5, color='gray', linestyle=':', linewidth=1, zorder=3)
    plt.title('Calculated vs Smartwatch Duration')
    plt.savefig('calculated_vs_smartwatch_duration.png',  bbox_inches='tight')
    plt.clf()


plot_sleep()
