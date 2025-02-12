import datetime
import math
import matplotlib.dates as mdates
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import process_data
import seaborn as sns
from matplotlib.lines import Line2D


def plot_sleep(filename="sleep.csv"):
    ry = 6.5  # red-yellow transition
    yg = 7.5  # yellow-green transition
    df = process_data.process_data(filename="sleep.csv")

    # plot duration vs date
    fig = plt.figure()
    plt.plot(df['date'], df['duration'], color='black')
    plt.scatter(df['date'], df['duration'], color='black')
    plt.xlabel('Date')
    plt.ylabel('Sleep Duration')
    plt.title('Sleep Duration Over Time')
    # Add horizontal lines at certain hours
    y_min, y_max = plt.ylim()
    plt.axhspan(yg, y_max, facecolor='lightgreen', alpha=0.5)
    plt.axhspan(ry, yg, facecolor='khaki', alpha=0.5)
    plt.axhspan(y_min, ry, facecolor='lightcoral', alpha=0.5)
    plt.ylim(y_min, y_max)
    # Set the tick locator to ensure proper spacing with a custom interval
    tick_interval = int(len(df['date']) / 7) + 1
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=tick_interval))
    # Set the tick formatter to display your desired date format
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # Rotate the tick labels for better readability
    plt.xticks(rotation=90)
    # Add exponential smoothing line
    df['duration_smooth'] = df['duration'].ewm(alpha=0.05, adjust=False).mean()
    plt.plot(df['date'], df['duration_smooth'], color='blue')
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
        if bin_edges[i+1] <= ry:
            colors.append('red')
        elif bin_edges[i] >= yg:
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
        if row['duration'] < ry:
            c = 'r'
        elif row['duration'] < yg:
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

    # Box plot of sleep duration with day of week as hue
    fig = plt.figure()
    ax = sns.boxplot(data=df, x='duration', y='day_of_week', order=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])
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

    ymin = 3.75
    ymax = 11.5

    # Background colors
    background_yellow_rect = patches.Rectangle((ymin, ymin), ymax - ymin, ymax - ymin, color='khaki', zorder=1)
    ax.add_patch(background_yellow_rect)

    green_vertices = [[ymax, ymax], [2 * yg - ymax, ymax], [ymax, 2 * yg - ymax]]
    green_triangle = patches.Polygon(green_vertices, closed=True, color='lightgreen', zorder=2)
    ax.add_patch(green_triangle)

    red_vertices = [[ymin, ymin], [2 * ry - ymin, ymin], [ymin, 2 * ry - ymin]]
    red_triangle = patches.Polygon(red_vertices, closed=True, color='lightcoral', zorder=2)
    ax.add_patch(red_triangle)

    colors = {'Good': 'b', 'Fair': 'k', 'Poor': 'r'}

    # Halo around most recent sleep session
    most_recent = df_notna.iloc[-1]
    ax.scatter(most_recent['duration'], most_recent['duration_smartwatch'], zorder=4, c='#FFFF14', s=100)
    ax.scatter(df_notna['duration'], df_notna['duration_smartwatch'], zorder=5, c=df_notna['rating_smartwatch'].map(colors))
    plt.xlabel('Calculated Duration')
    plt.ylabel('Smartwatch Duration')
    ax.set_xlim(ymin, ymax)
    ax.set_ylim(ymin, ymax)
    tick_labels = {
        4: '4:00',
        5: '5:00',
        6: '6:00',
        7: '7:00',
        8: '8:00',
        9: '9:00',
        10: '10:00',
        11: '11:00',
    }
    plt.xticks(ticks=list(tick_labels.keys()), labels=list(tick_labels.values()))
    plt.yticks(ticks=list(tick_labels.keys()), labels=list(tick_labels.values()))
    handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=v, label=k, markersize=8) for k, v in colors.items()]
    ax.legend(title='Sleep Rating', handles=handles, loc='upper left')
    # Dotted lines
    ax.plot([ymin, ymax], [ymin, ymax], color='blue', linestyle='--', zorder=4)
    ax.plot([ymin + 1, ymax], [ymin, ymax - 1], color='gray', linestyle='--', zorder=4)
    ax.plot([ymin + 2, ymax], [ymin, ymax - 2], color='gray', linestyle='--', zorder=4)
    ax.axhline(y=ry, color='gray', linestyle=':', linewidth=1, zorder=3)
    ax.axvline(x=ry, color='gray', linestyle=':', linewidth=1, zorder=3)
    ax.axhline(y=yg, color='gray', linestyle=':', linewidth=1, zorder=3)
    ax.axvline(x=yg, color='gray', linestyle=':', linewidth=1, zorder=3)
    plt.title('Calculated vs Smartwatch Duration')
    plt.savefig('calculated_vs_smartwatch_duration.png',  bbox_inches='tight')
    plt.clf()

    # Plot start time with moving average
    fig = plt.figure()
    plt.plot(df['date'], df['start_time_hr'], color='black')
    plt.scatter(df['date'], df['start_time_hr'], color='black')
    plt.xlabel('Date')
    plt.ylabel('Sleep Start Time')
    plt.title('Sleep Start Time Over Time')
    # Add horizontal lines at certain hours
    # y_min, y_max = plt.ylim()
    # plt.axhspan(yg, y_max, facecolor='lightgreen', alpha=0.5)
    # plt.axhspan(ry, yg, facecolor='khaki', alpha=0.5)
    # plt.axhspan(y_min, ry, facecolor='lightcoral', alpha=0.5)
    # plt.ylim(y_min, y_max)
    # x-ticks
    tick_interval = int(len(df['date']) / 7) + 1
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=tick_interval))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=90)
    # y-ticks
    tick_labels = {
        -3: '9:00pm',
        -2: '10:00pm',
        -1: '11:00pm',
        0: '12:00am',
        1: '1:00am',
        2: '2:00am',
    }
    plt.yticks(ticks=list(tick_labels.keys()), labels=list(tick_labels.values()))
    # Add exponential smoothing line
    df['start_smooth'] = df['start_time_hr'].ewm(alpha=0.05, adjust=False).mean()
    plt.plot(df['date'], df['start_smooth'], color='blue')
    plt.savefig('sleep_start_time.png',  bbox_inches='tight')
    plt.clf()

    # Sleep Start Time by Day of Week
    fig = plt.figure()
    ax = sns.boxplot(data=df, x='start_time_hr', y='day_of_week', order=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])
    plt.xlabel('Sleep Start Time')
    plt.ylabel('Day of Week')
    plt.title('Sleep Start Time by Day of Week')
    tick_labels = {
        -3: '9:00pm',
        -2: '10:00pm',
        -1: '11:00pm',
        0: '12:00am',
        1: '1:00am',
        2: '2:00am',
    }
    plt.xticks(ticks=list(tick_labels.keys()), labels=list(tick_labels.values()))
    plt.savefig('sleep_start_time_by_day_of_week.png',  bbox_inches='tight')
    plt.clf()


plot_sleep()
