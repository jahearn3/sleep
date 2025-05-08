import math
import matplotlib.dates as mdates
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import process_data
import seaborn as sns
from matplotlib.lines import Line2D


def plot_sleep_duration_over_time(df, ry, yg):
    # plot duration vs date
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
    plt.gca().xaxis.set_major_locator(
        mdates.DayLocator(interval=tick_interval)
    )
    # Set the tick formatter to display your desired date format
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # Rotate the tick labels for better readability
    plt.xticks(rotation=90)
    # Add exponential smoothing line
    df['duration_smooth'] = df['duration'].ewm(alpha=0.05, adjust=False).mean()
    plt.plot(df['date'], df['duration_smooth'], color='blue')
    plt.savefig('sleep_duration_over_time.png',  bbox_inches='tight')
    plt.clf()


def plot_sleep_duration_histogram(df, ry, yg, bin_interval=0.25):
    bin_min = math.floor(min(df['duration']) / bin_interval) * bin_interval
    bin_max = math.ceil(max(df['duration']) / bin_interval) * bin_interval
    bin_edges = np.arange(bin_min, bin_max + bin_interval, bin_interval)
    counts, _ = np.histogram(df['duration'], bins=bin_edges)
    colors = []
    for i in range(len(bin_edges) - 1):
        if bin_edges[i+1] <= ry:
            colors.append('red')
        elif bin_edges[i] >= yg:
            colors.append('green')
        else:
            colors.append('yellow')
    plt.bar(
        bin_edges[:-1], counts, width=np.diff(bin_edges), color=colors,
        edgecolor='black', alpha=0.5
    )
    plt.xlabel('Sleep Duration')
    plt.ylabel('Frequency')
    plt.title('Sleep Duration Histogram')
    plt.savefig('sleep_duration_histogram.png',  bbox_inches='tight')
    plt.clf()


def plot_sleep_times_each_day(df, ry, yg):
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
        11: '11:00',
    }
    plt.xticks(
        ticks=list(tick_labels.keys()),
        labels=list(tick_labels.values()),
        rotation=45
    )
    start_time_min = df['start_time_hr'].min() - 0.5
    stop_time_max = df['stop_time_hr'].max() + 0.5
    ax.set_xlim(start_time_min, stop_time_max)

    plt.xlabel('Time')
    plt.ylabel('Date')
    plt.title('Sleep Sessions')
    plt.savefig('sleep_times_each_day.png',  bbox_inches='tight')
    plt.clf()


def plot_sleep_duration_by_day_of_week(df, ry, yg):
    # Box plot of sleep duration with day of week as hue
    plt.figure()
    sns.boxplot(
        data=df,
        x='duration',
        y='day_of_week',
        order=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    )
    sns.swarmplot(
        data=df,
        x='duration',
        y='day_of_week',
        order=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        dodge=True
    )
    x_min, x_max = plt.xlim()
    plt.axvspan(yg, x_max, facecolor='lightgreen', alpha=0.5)
    plt.axvspan(ry, yg, facecolor='khaki', alpha=0.5)
    plt.axvspan(x_min, ry, facecolor='lightcoral', alpha=0.5)
    plt.xlim(x_min, x_max)
    plt.xlabel('Sleep Duration')
    plt.ylabel('Day of Week')
    plt.title('Sleep Duration by Day of Week')
    plt.savefig('sleep_duration_by_day_of_week.png',  bbox_inches='tight')
    plt.clf()


def plot_calculated_vs_smartwatch_duration(df_notna, ry, yg):
    # Plot comparing calculated duration to duration reported by smartwatch
    fig, ax = plt.subplots()

    ymin = 2.75
    ymax = 11.5

    # Background colors
    background_yellow_rect = patches.Rectangle(
        (ymin, ymin), ymax - ymin, ymax - ymin, color='khaki', zorder=1
    )
    ax.add_patch(background_yellow_rect)

    green_vertices = [
        [ymax, ymax],
        [2 * yg - ymax, ymax],
        [ymax, 2 * yg - ymax]
    ]
    green_triangle = patches.Polygon(
        green_vertices, closed=True, color='lightgreen', zorder=2
    )
    ax.add_patch(green_triangle)

    red_vertices = [[ymin, ymin], [2 * ry - ymin, ymin], [ymin, 2 * ry - ymin]]
    red_triangle = patches.Polygon(
        red_vertices, closed=True, color='lightcoral', zorder=2
    )
    ax.add_patch(red_triangle)

    colors = {'Good': 'b', 'Fair': 'k', 'Poor': 'r'}

    # Halo around most recent sleep session
    most_recent = df_notna.iloc[-1]
    ax.scatter(
        most_recent['duration'], most_recent['duration_smartwatch'],
        zorder=4, c='#FFFF14', s=100
    )
    ax.scatter(
        df_notna['duration'], df_notna['duration_smartwatch'],
        zorder=5, c=df_notna['rating_smartwatch'].map(colors), s=7
    )
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
    ticks = list(tick_labels.keys())
    labels = list(tick_labels.values())
    plt.xticks(ticks=ticks, labels=labels)
    # ticks = list(tick_labels.keys())
    # labels = list(tick_labels.values())
    plt.yticks(ticks=ticks, labels=labels)
    handles = [
        Line2D(
            [0], [0], marker='o', color='w', markerfacecolor=v, label=k,
            markersize=8
        )
        for k, v in colors.items()
    ]
    ax.legend(title='Sleep Rating', handles=handles, loc='upper left')
    # Dotted lines
    ax.plot([ymin, ymax], [ymin, ymax], color='blue', linestyle='--', zorder=4)
    ax.plot(
        [ymin + 1, ymax], [ymin, ymax - 1],
        color='gray', linestyle='--', zorder=4
    )
    ax.plot(
        [ymin + 2, ymax], [ymin, ymax - 2],
        color='gray', linestyle='--', zorder=4
    )
    ax.axhline(y=ry, color='gray', linestyle=':', linewidth=1, zorder=3)
    ax.axvline(x=ry, color='gray', linestyle=':', linewidth=1, zorder=3)
    ax.axhline(y=yg, color='gray', linestyle=':', linewidth=1, zorder=3)
    ax.axvline(x=yg, color='gray', linestyle=':', linewidth=1, zorder=3)
    plt.title('Calculated vs Smartwatch Duration')
    plt.savefig('calculated_vs_smartwatch_duration.png',  bbox_inches='tight')
    plt.clf()


def plot_sleep_start_time(df):
    # Plot start time with moving average
    plt.plot(df['date'], df['start_time_hr'], color='black')
    plt.scatter(df['date'], df['start_time_hr'], color='black')
    plt.xlabel('Date')
    plt.ylabel('Sleep Start Time')
    plt.title('Sleep Start Time Over Time')
    # x-ticks
    tick_interval = int(len(df['date']) / 7) + 1
    day_locator = mdates.DayLocator(interval=tick_interval)
    plt.gca().xaxis.set_major_locator(day_locator)
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
        3: '3:00am',
        4: '4:00am',
        5: '5:00am',
    }
    ticks = list(tick_labels.keys())
    labels = list(tick_labels.values())
    plt.yticks(ticks=ticks, labels=labels)
    # Add exponential smoothing line
    df['start_smooth'] = df['start_time_hr'].ewm(
        alpha=0.05, adjust=False
    ).mean()
    plt.plot(df['date'], df['start_smooth'], color='blue')
    plt.savefig('sleep_start_time.png',  bbox_inches='tight')
    plt.clf()


def plot_sleep_start_time_by_day_of_week(df):
    # Sleep Start Time by Day of Week
    plt.figure()
    sns.boxplot(
        data=df,
        x='start_time_hr',
        y='day_of_week',
        order=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    )
    sns.swarmplot(
        data=df,
        x='start_time_hr',
        y='day_of_week',
        dodge=True,
        order=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    )
    plt.xlabel('Sleep Start Time')
    plt.ylabel('Day of Week')
    plt.title('Sleep Start Time by Day of Week')
    tick_labels = {
        -3: '9:00pm',
        -2: '10:00',
        -1: '11:00',
        0: '12:00am',
        1: '1:00',
        2: '2:00',
        3: '3:00',
        4: '4:00',
        5: '5:00',
    }
    ticks = list(tick_labels.keys())
    labels = list(tick_labels.values())
    plt.xticks(ticks=ticks, labels=labels, rotation=90)
    plt.savefig('sleep_start_time_by_day_of_week.png',  bbox_inches='tight')
    plt.clf()
    # Print mean sleep start time for each day of the week
    median_start_times = df.groupby('day_of_week')['start_time_hr'].median()
    # Add 12 to each
    median_start_times = median_start_times.apply(
        lambda x: x + 12 if x < 0 else x
    )
    # Convert from decimal to hh:mm
    median_start_times = median_start_times.apply(
        lambda x: f"{int(x)}:{int((x - int(x)) * 60):02d}"
    )
    print("Median Sleep Start Time by Day of Week:")
    print(median_start_times)


def plot_sleep_score_histogram(df_notna):
    # Histogram of smartwatch score
    bin_interval = 5
    bin_min = 40
    bin_max = 100
    bin_edges = np.arange(bin_min, bin_max, bin_interval)
    counts, _ = np.histogram(df_notna['score_smartwatch'], bins=bin_edges)
    colors = []
    for i in range(len(bin_edges) - 1):
        if bin_edges[i+1] <= 60:
            colors.append('red')
        elif bin_edges[i] >= 80:
            colors.append('green')
        else:
            colors.append('yellow')
    plt.bar(bin_edges[:-1] + (bin_interval / 2),
            counts,
            width=np.diff(bin_edges),
            color=colors,
            edgecolor='black',
            alpha=0.5)
    plt.xlabel('Score according to Smartwatch')
    plt.ylabel('Frequency')
    plt.title('Sleep Score Histogram')
    plt.savefig('sleep_score_histogram.png',  bbox_inches='tight')
    plt.clf()


def plot_feature_correlation_matrix(correlation_matrix):
    # Visualize the correlation matrix
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f",
                cmap='coolwarm', vmin=-1, vmax=1, center=0,
                square=True, cbar_kws={"shrink": .8})
    plt.title('Feature Correlation Matrix')
    plt.savefig('feature_correlation_matrix.png',  bbox_inches='tight')
    plt.clf()


def plot_sleep_score_vs_duration_smartwatch(df_notna):
    # Scatter plot of duration_smartwatch vs score_smartwatch
    fig, ax = plt.subplots()
    colors = {'Good': 'c', 'Fair': 'gray', 'Poor': 'r'}
    # Halo around most recent sleep session
    most_recent = df_notna.iloc[-1]
    ax.scatter(
        most_recent['duration_smartwatch'],
        most_recent['score_smartwatch'],
        zorder=4,
        c='#FFFF14',
        s=100
    )
    ax.scatter(
        df_notna['duration_smartwatch'],
        df_notna['score_smartwatch'],
        zorder=5,
        c=df_notna['rating_smartwatch'].map(colors),
        s=10
    )
    plt.title('Sleep Score vs Duration')
    plt.xlabel('Smartwatch Duration (hours)')
    plt.ylabel('Sleep Score')
    handles = [
        Line2D(
            [0], [0], marker='o', color='w', markerfacecolor=v, label=k,
            markersize=8
        )
        for k, v in colors.items()
    ]
    plt.legend(title='Sleep Rating', handles=handles, loc='upper left')
    plt.savefig('sleep_score_vs_duration.png',  bbox_inches='tight')
    plt.clf()


def plot_sleep_score_vs_day_of_week(df):
    # Box plot of sleep score with day of week as hue
    plt.figure()
    sns.boxplot(
        data=df,
        x='score_smartwatch',
        y='day_of_week',
        order=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    )
    sns.swarmplot(
        data=df,
        x='score_smartwatch',
        y='day_of_week',
        order=['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        dodge=True)
    x_min, x_max = plt.xlim()
    plt.axvspan(80, x_max, facecolor='lightgreen', alpha=0.5)
    plt.axvspan(60, 80, facecolor='khaki', alpha=0.5)
    plt.axvspan(x_min, 60, facecolor='lightcoral', alpha=0.5)
    plt.xlim(x_min, x_max)
    plt.xlabel('Sleep Score')
    plt.ylabel('Day of Week')
    plt.title('Sleep Score by Day of Week')
    plt.savefig('sleep_score_by_day_of_week.png',  bbox_inches='tight')
    plt.clf()


def plot_sleep(filename="sleep.csv"):
    ry = 6.5  # red-yellow transition
    yg = 7.5  # yellow-green transition
    df = process_data.process_data(filename="sleep.csv")

    # Drop null values
    df_notna = df.dropna(subset=['duration_smartwatch'])

    # Convert duration_smartwatch to float
    df_notna.loc[:, 'duration_smartwatch'] = df_notna[
        'duration_smartwatch'
    ].apply(
        lambda x: (
            int(x.split(':')[0]) + int(x.split(':')[1]) / 60.0
        ) if isinstance(x, str) else 0
    )

    plot_sleep_duration_over_time(df, ry, yg)
    plot_sleep_duration_histogram(df, ry, yg)
    plot_sleep_times_each_day(df, ry, yg)
    plot_sleep_duration_by_day_of_week(df, ry, yg)
    plot_calculated_vs_smartwatch_duration(df_notna, ry, yg)
    plot_sleep_start_time(df)
    plot_sleep_start_time_by_day_of_week(df)
    plot_sleep_score_histogram(df_notna)
    plot_sleep_score_vs_duration_smartwatch(df_notna)
    plot_sleep_score_vs_day_of_week(df)


plot_sleep()
