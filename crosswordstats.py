import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from matplotlib.animation import FuncAnimation, PillowWriter
import time
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
    plt.plot(x, times, 'o', [x[i] for i in dates_indices], best_fit_fn(dates_indices),  ms=3)
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
            plt.plot([x[i] for i in indices], best_fit_fn(indices), label=weekday,  ms=3)
    plt.plot(x, times, 'o', ms=3)
    plt.gcf().autofmt_xdate()
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: time.strftime('%M:%S', time.gmtime(s)))
    ax.yaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    plt.title(f"Best Fit Curve by Day for {name} of Degree {degree}")
    plt.legend()
    plt.ylim(top = max([valid_time for valid_time in times if valid_time]) + 10, bottom=0)
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
        ax.annotate(np.round(p.get_height(), decimals=2), (p.get_x()+p.get_width()/2., p.get_height()),
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
        ax.annotate(np.round(p.get_height(), decimals=2), (p.get_x()+p.get_width()/2., p.get_height()),
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
    datetimes = [dt.datetime(int(date.split('/')[2]),int(date.split('/')[0]), int(date.split('/')[1])) for date in dates]
    series = pd.Series(data=daily_weights, index=datetimes)
    cmap = matplotlib.colors.ListedColormap(['grey', 'skyblue', 'navajowhite', 'palegreen', 'lightcoral', 'plum'])
    fig, ax = calmap.calendarplot(series, fillcolor='silver', cmap=cmap, fig_kws=dict(figsize=(10,4)))
    labels = ['Tie'] + names
    formatter = plt.FuncFormatter(lambda val, loc: labels[int(val)])
    fig.colorbar(ax[0].get_children()[1], ax=ax.ravel().tolist(), shrink=0.4, format=formatter)
    plt.savefig(filename)
    plt.close('all')

def total_wins_plot(overall_dict, dates, filename):
    fig, ax = plt.subplots()
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
                wins_dict[name].append(total+1)
            else:
                wins_dict[name].append(total)

    datetimes = [dt.datetime(int(date.split('/')[2]),int(date.split('/')[0]), int(date.split('/')[1])) for date in dates]
    for name in wins_dict:
        plt.plot(datetimes, wins_dict[name], '-', label=name, ms=3)
    plt.gcf().autofmt_xdate()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    plt.title("Cumulative Wins")
    plt.legend()
    plt.xlabel('Day')
    plt.ylabel('Wins')
    plt.grid(b=True, which='both')
    plt.savefig(filename, dpi=500)
    plt.close('all')

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
                wins_dict[name].append(total+1)
            else:
                wins_dict[name].append(total)

    fig, ax = plt.subplots(figsize=(8,6))
    seconds = 15
    total_kb = 10000
    frames = len(dates)
    fps = frames/(seconds) # animation will always be 30 seconds
    kbs = total_kb/seconds
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
    ax.pie(wins, labels=names, explode=[0.01]*len(wins), autopct='%1.1f%%', startangle=90)
    ax.set_title(dates[num])


def total_time_plot(overall_dict, dates, filename):
    fig, ax = plt.subplots()
    times_dict = {name: [] for name in overall_dict}
    for name in overall_dict:
        for day_index in range(len(dates)):
            if overall_dict[name][day_index] is None:
                times_dict[name].append(None)
            else:
                current_sum = overall_dict[name][day_index]
                if len(times_dict[name]) == 0:
                    times_dict[name].append(current_sum)
                else:
                    last_time_index = day_index - 1
                    while last_time_index > 0 and times_dict[name][last_time_index] is None:
                        last_time_index -= 1
                    if last_time_index > 0:
                        current_sum += times_dict[name][last_time_index]
                    elif times_dict[name][0] is not None:
                        current_sum += times_dict[name][0]
                    times_dict[name].append(current_sum)
        missed_days = times_dict[name].count(None)
        times = [seconds for seconds in overall_dict[name] if seconds is not None]
        average = sum(times)/len(times)
        print(f'{name} -  Average: {average}')
        print(f'{name} -  Missed Days: {missed_days}')
        missed_day_sum = missed_days * average
        print(f'{name} -  Missed Days * Average: {missed_day_sum}')
        last_time_index = len(times_dict[name]) - 1
        while last_time_index > 0 and times_dict[name][last_time_index] is None:
            last_time_index -= 1
        if last_time_index > 0:
            print(f'{name} -  Last Sum: {times_dict[name][last_time_index]}')
            missed_day_sum += times_dict[name][last_time_index]
        elif times_dict[name][0] is not None:
            missed_day_sum += times_dict[name][0]
        times_dict[name].append(missed_day_sum)

    datetimes = [dt.datetime(int(date.split('/')[2]),int(date.split('/')[0]), int(date.split('/')[1])) for date in dates]
    last_date = dates[-1]
    last_datetime = dt.datetime(int(last_date.split('/')[2]), int(last_date.split('/')[0]),
                                int(last_date.split('/')[1]))
    next_datetime = last_datetime + dt.timedelta(days=1)
    datetimes.append(next_datetime)
    for name in times_dict:
        plt.plot(datetimes, times_dict[name], '.-', label=name, ms=3)
    plt.gcf().autofmt_xdate()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: str(dt.timedelta(seconds=s)))
    ax.yaxis.set_major_formatter(formatter)
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    plt.title(r"Cumulative Time (with Missed Days × Average Time appended)")
    plt.legend()
    plt.xlabel('Day')
    plt.ylabel('Time')
    plt.grid(b=True, which='both')
    plt.tight_layout()
    plt.savefig(filename, dpi=500)
    plt.close('all')
