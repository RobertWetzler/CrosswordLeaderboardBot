import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from matplotlib.animation import FuncAnimation, PillowWriter
import time
import itertools
import datetime as dt
import pandas as pd
import numpy as np
import calmap
from matplotlib.ticker import MultipleLocator, AutoMinorLocator


def lineplot(overall_dict, date_list, filename, ylim=None, daysBack=None):
    fig, ax = plt.subplots()
    dates = list(date_list)
    if daysBack:
        dates = dates[-daysBack:]
    x = [dt.datetime.strptime(d, '%m/%d/%Y').date() for d in dates]
    for name in overall_dict:
        times = list(overall_dict[name])
        if daysBack:
            times = overall_dict[name][-daysBack:]
        plt.plot(x, times, 'o-', label=name, ms=3)
    plt.gcf().autofmt_xdate()
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: time.strftime('%M:%S', time.gmtime(s)))
    ax.yaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    plt.title("Doobie Brothers Crossword Times")
    plt.legend()
    plt.xlabel('Day')
    plt.ylabel('Time')
    if ylim is not None:
        plt.ylim(top=ylim)
    plt.savefig(filename, dpi=500)
    plt.close('all')


def lineplot_best_fit(overall_dict, date_list, filename, name, degree):
    fig, ax = plt.subplots()
    dates = list(date_list)
    x = [dt.datetime.strptime(d, '%m/%d/%Y').date() for d in dates]
    times = list(overall_dict[name])
    dates_indices = list()
    for i in range(len(times)):
        if times[i]:
            dates_indices.append(i)
    coef = np.polyfit(dates_indices, [times[i] for i in dates_indices], degree)
    best_fit_fn = np.poly1d(coef)
    plt.plot(x, times, 'o', [x[i] for i in dates_indices], best_fit_fn(dates_indices), ms=3)
    plt.gcf().autofmt_xdate()
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: time.strftime('%M:%S', time.gmtime(s)))
    ax.yaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    plt.title(f"Best Fit Curve for {name} of Degree {degree}")
    plt.xlabel('Day')
    plt.ylabel('Time')
    plt.savefig(filename, dpi=500)
    plt.close('all')


def lineplot_best_fit_week(overall_dict, date_list, filename, name, degree):
    fig, ax = plt.subplots()
    dates = list(date_list)
    day_times = dict()
    day_indices = dict()
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    x = [dt.datetime.strptime(d, '%m/%d/%Y').date() for d in dates]
    times = list(overall_dict[name])
    for day_index in range(len(times)):
        day_list = dates[day_index].split('/')
        day_num = dt.datetime(int(day_list[2]), int(day_list[0]), int(day_list[1])).weekday()
        if times[day_index]:
            if weekdays[day_num] not in day_times:
                day_times[weekdays[day_num]] = list()
            if weekdays[day_num] not in day_indices:
                day_indices[weekdays[day_num]] = list()
            day_times[weekdays[day_num]].append(times[day_index])
            day_indices[weekdays[day_num]].append(day_index)
    for weekday in weekdays:
        if weekday in day_times:
            coef = np.polyfit(day_indices[weekday], day_times[weekday], degree)
            best_fit_fn = np.poly1d(coef)
            indices = [i for i in range(len(x)) if (day_indices[weekday][0] <= i <= day_indices[weekday][-1])]
            plt.plot([x[i] for i in indices], best_fit_fn(indices), label=weekday, ms=3)
    plt.plot(x, times, 'o', ms=3)
    plt.gcf().autofmt_xdate()
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: time.strftime('%M:%S', time.gmtime(s)))
    ax.yaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    plt.title(f"Best Fit Curve by Day for {name} of Degree {degree}")
    plt.legend()
    plt.ylim(top=max([valid_time for valid_time in times if valid_time]) + 10, bottom=0)
    plt.xlabel('Day')
    plt.ylabel('Time')
    plt.savefig(filename, dpi=500)
    plt.close('all')


def lineplot_best(overall_dict, dates, filename, ylim=None):
    fig, ax = plt.subplots()
    x = [dt.datetime.strptime(d, '%m/%d/%Y').date() for d in dates]
    x_non = []
    x_sat = []
    best_non = []
    best_sat = []
    for name in overall_dict:
        for i in range(len(overall_dict[name])):
            x_curr, best_curr, idx = (x_sat, best_sat, i // 7) if i % 7 == 3 else (x_non, best_non, i - (i + 4) // 7)
            if (len(best_non) + len(best_sat)) < len(overall_dict[name]):
                best_curr.append(overall_dict[name][i])
                x_curr.append(x[i])
            elif overall_dict[name][i] is not None and best_curr[idx] > overall_dict[name][i]:
                best_curr[idx] = overall_dict[name][i]
    plt.plot(x_non, best_non, 'o-k', label="Mini Crosswords", ms=3)
    plt.plot(x_sat, best_sat, 'o-b', label="Saturday Midi's", ms=3)

    plt.gcf().autofmt_xdate()
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: time.strftime('%M:%S', time.gmtime(s)))
    ax.yaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    plt.title("Best of The Doobies")
    plt.legend()
    plt.xlabel('Day')
    plt.ylabel('Time')
    if ylim is not None:
        plt.ylim(top=ylim)
    plt.savefig(filename, dpi=500)
    plt.close('all')


def avgtimes(overall_dict, dates, filename):
    week_avgs = dict()
    for name in overall_dict:
        week_avgs[name] = dict()
        week_avgs[name]['avgs'] = [0] * 7
        week_avgs[name]['counts'] = [0] * 7
        for day_index in range(len(overall_dict[name])):
            day_list = dates[day_index].split('/')
            day = (dt.datetime(int(day_list[2]), int(day_list[0]), int(day_list[1])).weekday() + 1) % 7
            if overall_dict[name][day_index] is not None:
                week_avgs[name]['avgs'][day] += overall_dict[name][day_index]
                week_avgs[name]['counts'][day] += 1
        for weekday in range(len(week_avgs[name]['avgs'])):
            if week_avgs[name]['counts'][weekday] != 0:
                week_avgs[name]['avgs'][weekday] /= week_avgs[name]['counts'][weekday]
            else:
                week_avgs[name]['avgs'][weekday] = None

    labels = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    everyone = list()
    fig, ax = plt.subplots()
    for name in week_avgs:
        everyone.append(week_avgs[name]['avgs'])
    df = pd.DataFrame(everyone, columns=labels)
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: time.strftime('%M:%S', time.gmtime(s)))
    ax.yaxis.set_major_formatter(formatter)
    df.T.plot.bar(ax=ax)
    ax.legend([name for name in overall_dict])
    for p in ax.patches:
        ax.annotate(np.round(p.get_height(), decimals=2), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 6), textcoords='offset points', fontsize='x-small')
    plt.title("Average Crossword Times by Day of the Week")
    plt.gcf().autofmt_xdate()
    plt.savefig(filename, dpi=500)
    plt.close('all')


def best_times(min_dict, filename):
    labels = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    # Doobie order
    names = list(min_dict.keys())
    if set(names) == {'Robert', 'Macey', 'Levi', 'Max', 'Asher'}:
        names = ['Max', 'Macey', 'Asher', 'Robert', 'Levi']
    everyone = [[min_dict[name].get(day, None) for day in labels] for name in names]
    fig, ax = plt.subplots()
    df = pd.DataFrame(everyone, columns=labels)
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: time.strftime('%M:%S', time.gmtime(s)))
    ax.yaxis.set_major_formatter(formatter)
    df.T.plot.bar(ax=ax)
    ax.legend(names)
    for p in ax.patches:
        ax.annotate(np.round(p.get_height(), decimals=2), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 6), textcoords='offset points', fontsize='x-small')
    plt.title("Best Crossword Times by Day of the Week")
    plt.gcf().autofmt_xdate()
    plt.savefig(filename, dpi=800)
    plt.close('all')


def calendar_plot(overall_dict, dates, filename):
    names = list(overall_dict.keys())
    weights = [i + 1 for i in range(len(names))]
    daily_weights = list()
    for day_index in range(len(dates)):
        min = 999999
        weight = None
        for name in names:
            if overall_dict[name][day_index] is not None:
                if overall_dict[name][day_index] < min:
                    min = overall_dict[name][day_index]
                    weight = weights[names.index(name)]
                elif overall_dict[name][day_index] == min:
                    weight = 0
        daily_weights.append(weight)
    datetimes = [dt.datetime(year=int(date.split('/')[2]), month=int(date.split('/')[0]), day=int(date.split('/')[1])) for date in
                 dates]
    series = pd.Series(data=daily_weights, index=datetimes)
    cmap = matplotlib.colors.ListedColormap(['grey', 'skyblue', 'navajowhite', 'palegreen', 'lightcoral', 'plum'])
    fig, ax = calmap.calendarplot(series, fillcolor='silver', cmap=cmap, fig_kws=dict(figsize=(10, 4)))
    labels = ['Tie'] + names
    formatter = plt.FuncFormatter(lambda val, loc: labels[int(val)])
    fig.colorbar(ax[0].get_children()[1], ax=ax.ravel().tolist(), shrink=0.4, format=formatter)
    plt.savefig(filename)
    plt.close('all')


def total_wins_plot(overall_dict, dates, filename, past_month=False, past_year=False):
    fig, ax = plt.subplots()
    wins_dict = {name: [] for name in overall_dict}
    if past_month or past_year:
        # (last date string)
        lds = [int(s) for s in dates[-1].split('/')]
        last_date = dt.datetime(year=int(lds[2]), month=int(lds[0]), day=int(lds[1]))
        # first date of the month/year
        first_date = dt.datetime(year=lds[2], month=1, day=1)
        if past_month:
            first_date = dt.datetime(year=lds[2], month=lds[0], day=1)
        delta = (last_date - first_date).days
        start = len(dates) - 1 - delta
    else:
        start = 0
    for day_index in range(start, len(dates)):
        min_time = None
        min_names = []
        for name in overall_dict:
            if overall_dict[name][day_index] is not None:
                if min_time is None:
                    min_time = overall_dict[name][day_index]
                    min_names = [name]
                elif overall_dict[name][day_index] < min_time:
                    min_time = overall_dict[name][day_index]
                    min_names = [name]
                elif overall_dict[name][day_index] == min_time:
                    min_names.append(name)
        for name in overall_dict:
            if len(wins_dict[name]) == 0:
                total = 0
            else:
                total = wins_dict[name][-1]
            if name in min_names:
                wins_dict[name].append(total + 1)
            else:
                wins_dict[name].append(total)

    datetimes = [dt.datetime(int(date.split('/')[2]), int(date.split('/')[0]), int(date.split('/')[1])) for date in
                 dates[start:]]
    for name in wins_dict:
        plt.plot(datetimes, wins_dict[name], '-', label=name, ms=3)
        plt.text(datetimes[-1], wins_dict[name][-1], wins_dict[name][-1])
    plt.gcf().autofmt_xdate()
    if len(datetimes) <= 5:
        ax.xaxis.set_major_locator(mdates.DayLocator())
    else:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    title = 'Cumulative Wins'
    if past_month:
        lds = [int(s) for s in dates[-1].split('/')]
        last_date = dt.datetime(year=int(lds[2]), month=int(lds[0]), day=int(lds[1]))
        # Gets month name
        month = last_date.strftime("%B")
        title += f' for {month}'
    elif past_year:
        lds = [int(s) for s in dates[-1].split('/')]
        last_date = dt.datetime(year=int(lds[2]), month=int(lds[0]), day=int(lds[1]))
        # Gets month name
        year = last_date.strftime("%Y")
        title += f' for {year}'
    plt.title(title)
    plt.legend()
    plt.xlabel('Day')
    plt.ylabel('Wins')
    plt.grid(b=True, which='both')
    plt.savefig(filename, dpi=500)
    plt.close('all')
    return wins_dict


def pie_plot(leaderboard_dict, filename):
    labels = [name for name in leaderboard_dict]
    sizes = [wins for wins in leaderboard_dict.values()]
    plt.pie(sizes, labels=labels, startangle=90, autopct='%1.1f%%')
    plt.axis('equal')
    plt.title('Pie Chart of Leaderboard')
    plt.savefig(filename, dpi=500)
    plt.close('all')


def pie_time_plot(overall_dict, dates, filename):
    wins_dict = {name: [] for name in overall_dict}
    for day_index in range(len(dates)):
        min_time = None
        min_names = []
        for name in overall_dict:
            if overall_dict[name][day_index] is not None:
                if min_time is None:
                    min_time = overall_dict[name][day_index]
                    min_names = [name]
                elif overall_dict[name][day_index] < min_time:
                    min_time = overall_dict[name][day_index]
                    min_names = [name]
                elif overall_dict[name][day_index] == min_time:
                    min_names.append(name)
        for name in overall_dict:
            if len(wins_dict[name]) == 0:
                total = 0
            else:
                total = wins_dict[name][-1]
            if name in min_names:
                wins_dict[name].append(total + 1)
            else:
                wins_dict[name].append(total)

    fig, ax = plt.subplots(figsize=(8, 6))
    seconds = 15
    total_kb = 10000
    frames = len(dates)
    fps = frames / (seconds)  # animation will always be 30 seconds
    kbs = total_kb / seconds
    ani = FuncAnimation(fig, _update, frames=frames, repeat=False, fargs=(wins_dict, dates, ax), repeat_delay=1000)
    writer = PillowWriter(fps=fps, bitrate=kbs, metadata={'title': 'Pie Chart Gif'})
    ani.save(filename, writer=writer)
    plt.close('all')


def _update(num, *fargs):
    wins_dict = fargs[0]
    dates = fargs[1]
    ax = fargs[2]
    ax.clear()
    ax.axis('equal')
    wins = [wins_dict[name][num] for name in wins_dict if wins_dict[name][num] != 0]
    names = [f'{name} ({wins_dict[name][num]})' for name in wins_dict if wins_dict[name][num] != 0]
    ax.pie(wins, labels=names, explode=[0.01] * len(wins), autopct='%1.1f%%', startangle=90)
    ax.set_title(dates[num])


def total_time_plot(overall_dict, dates, filename, past_month=False, past_year=False):
    fig, ax = plt.subplots()
    times_dict = {name: [] for name in overall_dict}
    if past_month or past_year:
        # (last date string)
        lds = [int(s) for s in dates[-1].split('/')]
        last_date = dt.datetime(year=int(lds[2]), month=int(lds[0]), day=int(lds[1]))
        # first date of the month/year
        first_date = dt.datetime(year=lds[2], month=1, day=1)
        if past_month:
            first_date = dt.datetime(year=lds[2], month=lds[0], day=1)
        delta = (last_date - first_date).days
        start = len(dates) - 1 - delta
    else:
        start = 0
    for name in overall_dict:
        for day_index in range(start, len(dates)):
            if overall_dict[name][day_index] is None:
                times_dict[name].append(None)
            else:
                times_dict[name].append(sum(t for t in overall_dict[name][start:day_index + 1] if t is not None))
            """ The following is poopcode, but its poopcode that should run in O(n)
            if overall_dict[name][day_index] is None:
                times_dict[name].append(None)
            else:
                current_sum = overall_dict[name][day_index]
                if len(times_dict[name]) == 0:
                    times_dict[name].append(current_sum)
                else:
                    last_time_index = day_index - 1
                    print(f'Out loop {last_time_index}')
                    while last_time_index >= start and times_dict[name][last_time_index-start] is None:
                        last_time_index -= 1
                        print(f'In loop {last_time_index}')
                    if last_time_index >= start:
                        current_sum += times_dict[name][last_time_index]
                    elif times_dict[name][0] is not None:
                        current_sum += times_dict[name][start]
                    times_dict[name].append(current_sum)"""
        missed_days = times_dict[name].count(None)
        times = [seconds for seconds in overall_dict[name] if seconds is not None]
        average = sum(times) / len(times)
        missed_day_sum = missed_days * average
        last_time_index = len(times_dict[name]) - 1
        while last_time_index > 0 and times_dict[name][last_time_index] is None:
            last_time_index -= 1
        if last_time_index > 0:
            missed_day_sum += times_dict[name][last_time_index]
        elif times_dict[name][0] is not None:
            missed_day_sum += times_dict[name][0]
        times_dict[name].append(missed_day_sum)

    datetimes = [dt.datetime(int(date.split('/')[2]), int(date.split('/')[0]), int(date.split('/')[1])) for date in
                 dates[start:]]
    last_date = dates[-1]
    last_datetime = dt.datetime(int(last_date.split('/')[2]), int(last_date.split('/')[0]),
                                int(last_date.split('/')[1]))
    next_datetime = last_datetime + dt.timedelta(days=1)
    datetimes.append(next_datetime)
    for name in times_dict:
        plt.plot(datetimes, times_dict[name], '.-', label=name, ms=3)
        plt.text(datetimes[-1], times_dict[name][-1], str(dt.timedelta(seconds=int(times_dict[name][-1]))))
    plt.gcf().autofmt_xdate()
    if len(datetimes) <= 5:
        ax.xaxis.set_major_locator(mdates.DayLocator())
    else:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: str(dt.timedelta(seconds=s)))
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    title = r'Cumulative Time (with Missed Days × Average Time appended)'
    if past_month:
        lds = [int(s) for s in dates[-1].split('/')]
        last_date = dt.datetime(year=int(lds[2]), month=int(lds[0]), day=int(lds[1]))
        # Gets month name
        month = last_date.strftime("%B")
        title += f' for {month}'
    elif past_year:
        lds = [int(s) for s in dates[-1].split('/')]
        last_date = dt.datetime(year=int(lds[2]), month=int(lds[0]), day=int(lds[1]))
        # Gets month name
        year = last_date.strftime("%Y")
        title += f' for {year}'
    plt.title(title)
    plt.legend()
    plt.xlabel('Day')
    plt.ylabel('Time')
    plt.grid(b=True, which='both')
    plt.tight_layout()
    plt.savefig(filename, dpi=500)
    plt.close('all')


def histogram(overall_dict, filename, n_bins):
    fig, ax = plt.subplots()
    bin = np.arange(n_bins)
    range = (0, 60)
    times = [[t for t in overall_dict[name] if t is not None] for name in overall_dict]
    plt.hist(times, bin, range=range, histtype='bar', label=list((overall_dict.keys())))
    plt.legend()
    plt.title('Histogram of Submitted Times')
    plt.savefig(filename, dpi=500)
    plt.close('all')


def violin_plot(overall_dict, dates, filename):
    fig, ax = plt.subplots()
    plt.title('Violin Plot')
    sns.set(style='whitegrid', palette='pastel', color_codes=True)
    # Create name column
    # List of each name * number of items stored under that name
    name_col = list(itertools.chain.from_iterable([[n] * len(overall_dict[n]) for n in overall_dict]))
    # Create time column
    time_col = [t for n in overall_dict for t in overall_dict[n]]
    # Create saturday column
    datetimes = [dt.datetime.strptime(d, '%m/%d/%Y').date() for d in dates]
    saturday_col = ['Yes' if d.weekday() == 5 else 'No' for d in datetimes * len(overall_dict)]
    data = pd.DataFrame(data={'Name': name_col, 'Time': time_col, 'Saturday': saturday_col})
    # Create violin plot
    sns_plot = sns.violinplot(x='Name', y='Time', hue='Saturday', split=True, inner='quart',
                              pallete={'Yes': 'y', 'No': 'b'},
                              cut=0,
                              data=data)
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: time.strftime('%M:%S', time.gmtime(s)))
    ax.yaxis.set_major_formatter(formatter)
    sns_fig = sns_plot.get_figure()
    plt.grid(b=True, axis='y')
    sns_fig.savefig(filename)
    plt.close('all')


def swarm_plot(overall_dict, dates, filename, past_month=False, past_year=False):
    fig, ax = plt.subplots(figsize=(12, 5))
    plt.title('Swarm Plot')
    sns.set(style='whitegrid', color_codes=True)
    start = 0
    if past_month or past_year:
        # (last date string)
        lds = [int(s) for s in dates[-1].split('/')]
        last_date = dt.datetime(year=int(lds[2]), month=int(lds[0]), day=int(lds[1]))
        # first date of the month/year
        first_date = dt.datetime(year=lds[2], month=1, day=1)
        if past_month:
            first_date = dt.datetime(year=lds[2], month=lds[0], day=1)
        delta = (last_date - first_date).days
        start = len(dates) - 1 - delta

    # Create name column
    # List of each name * number of items stored under that name
    name_col = list(itertools.chain.from_iterable([[n] * len(overall_dict[n][start:]) for n in overall_dict]))
    # Create time column
    time_col = [t for n in overall_dict for t in overall_dict[n][start:]]
    # Create saturday column
    datetimes = [dt.datetime.strptime(d, '%m/%d/%Y').date() for d in dates[start:]]
    saturday_col = ['Yes' if d.weekday() == 5 else 'No' for d in datetimes * len(overall_dict)]
    data = pd.DataFrame(data={'Name': name_col, 'Time': time_col, 'Saturday': saturday_col})
    # Create swarm plot
    sns_plot = sns.swarmplot(x='Name', y='Time', hue='Saturday', data=data, size=3)
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: time.strftime('%M:%S', time.gmtime(s)))
    ax.yaxis.set_major_formatter(formatter)
    sns_fig = sns_plot.get_figure()
    plt.grid(b=True, axis='y')
    sns_fig.savefig(filename)
    plt.close('all')


def rankings_plot(overall_dict, dates, filename, past_month=False, past_year=False):
    fig, ax = plt.subplots()
    scores = [10, 8, 5, 3, 1]
    rank_dict = {name: [] for name in overall_dict}
    start = 0
    if past_month or past_year:
        # (last date string)
        lds = [int(s) for s in dates[-1].split('/')]
        last_date = dt.datetime(year=int(lds[2]), month=int(lds[0]), day=int(lds[1]))
        # first date of the month/year
        first_date = dt.datetime(year=lds[2], month=1, day=1)
        if past_month:
            first_date = dt.datetime(year=lds[2], month=lds[0], day=1)
        delta = (last_date - first_date).days
        start = len(dates) - 1 - delta
    for day_index in range(start, len(dates)):
        daily_rank = []
        did_not_play = []
        for name in overall_dict:
            user_time = overall_dict[name][day_index]
            if user_time is None:
                did_not_play.append(name)
            elif len(daily_rank) == 0:
                daily_rank.append([name])
            else:
                # iterate rank to insert name
                i = 0
                inserted = False
                while i < len(daily_rank) and not inserted:
                    if user_time < overall_dict[daily_rank[i][0]][day_index]:
                        daily_rank.insert(i, [name])
                        inserted = True
                    elif user_time == overall_dict[daily_rank[i][0]][day_index]:
                        daily_rank[i].append(name)
                        inserted = True
                    else:
                        i += 1
                if not inserted:
                    daily_rank.append([name])
        # distribute scores. Ties mean they get assigned the average of their place - two first means (10 + 8) // 2
        scores_copy = list(scores)
        mg = ''
        for place in daily_rank:
            score = 0
            for i in range(len(place)):
                score += scores_copy.pop(0)
            # Take average for ties
            score //= len(place)
            # Add score to rank_dict list
            for name in place:
                if len(rank_dict[name]) == 0:
                    total = 0
                else:
                    total = rank_dict[name][-1]
                rank_dict[name].append(total + score)
                mg += f'{name}: {score} '
        for name in did_not_play:
            if len(rank_dict[name]) == 0:
                total = 0
            else:
                total = rank_dict[name][-1]
            rank_dict[name].append(total)
            mg += f'{name}: {0} '

    datetimes = [dt.datetime(int(date.split('/')[2]), int(date.split('/')[0]), int(date.split('/')[1])) for date in
                 dates[start:]]
    for name in rank_dict:
        plt.plot(datetimes, rank_dict[name], '-', label=name, ms=3)
    plt.gcf().autofmt_xdate()
    # Avoid duplicate day ticks
    if len(datetimes) <= 5:
        ax.xaxis.set_major_locator(mdates.DayLocator())
    else:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    title = 'Ranked rankings'
    if past_month:
        lds = [int(s) for s in dates[-1].split('/')]
        last_date = dt.datetime(year=int(lds[2]), month=int(lds[0]), day=int(lds[1]))
        # Gets month name
        month = last_date.strftime("%B")
        title += f' for {month}'
    elif past_year:
        lds = [int(s) for s in dates[-1].split('/')]
        last_date = dt.datetime(year=int(lds[2]), month=int(lds[0]), day=int(lds[1]))
        # Gets month name
        year = last_date.strftime("%Y")
        title += f' for {year}'
    plt.title(title)
    plt.legend()
    plt.xlabel('Day')
    plt.ylabel('Rank')
    plt.grid(b=True, which='both')
    plt.savefig(filename, dpi=500)
    plt.close('all')
    return {name: scores[-1] for (name, scores) in rank_dict.items()}


def percentage_plot(overall_dict, dates, filename):
    fig, ax = plt.subplots()
    wins_dict = {name: [] for name in overall_dict}
    perc_dict = {name: [] for name in overall_dict}
    for day_index in range(len(dates)):
        min_time = None
        min_names = []
        for name in overall_dict:
            if overall_dict[name][day_index] is not None:
                if min_time is None:
                    min_time = overall_dict[name][day_index]
                    min_names = [name]
                elif overall_dict[name][day_index] < min_time:
                    min_time = overall_dict[name][day_index]
                    min_names = [name]
                elif overall_dict[name][day_index] == min_time:
                    min_names.append(name)
        for name in overall_dict:
            if len(wins_dict[name]) == 0:
                total = 0
            else:
                total = wins_dict[name][-1]
            if name in min_names:
                wins_dict[name].append(total + 1)
            else:
                wins_dict[name].append(total)
        sum_wins = sum(wins_dict[name][-1] for name in wins_dict)
        for name in overall_dict:
            perc_dict[name].append(100 * wins_dict[name][-1] / sum_wins)

    datetimes = [dt.datetime(int(date.split('/')[2]), int(date.split('/')[0]), int(date.split('/')[1])) for date in
                 dates]
    for name in wins_dict:
        plt.plot(datetimes, perc_dict[name], '-', label=name, ms=3)
    plt.gcf().autofmt_xdate()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    plt.title("Percentage of Leaderboard Over Time")
    plt.legend()
    plt.xlabel('Day')
    plt.ylabel('Percentage of Leaderboard')
    plt.grid(b=True, which='both')
    plt.savefig(filename, dpi=500)
    plt.close('all')
