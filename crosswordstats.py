import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import time
import datetime as dt
import pandas as pd
import numpy as np
import calmap

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
            elif overall_dict[name][i] != None and best_curr[idx] > overall_dict[name][i]:
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
                week_avgs[name]['avgs'][day] += overall_dict[name][day_index] + 1
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
    list_of_lists = list(list())
    df = pd.DataFrame(everyone, columns=labels)
    formatter = matplotlib.ticker.FuncFormatter(lambda s, y: time.strftime('%M:%S', time.gmtime(s)))
    ax.yaxis.set_major_formatter(formatter)
    df.T.plot.bar(ax=ax)
    ax.legend([name for name in overall_dict])
    plt.title("Average Crossword Times per Day of the Week")
    plt.gcf().autofmt_xdate()
    plt.savefig(filename, dpi=500)

def calendar_plot(overall_dict, dates, filename):
    names = list(overall_dict.keys())
    weights = [i + 1 for i in range(len(names))]
    daily_weights = list()
    for day_index in range(len(dates)):
        min = 999999
        weight = None
        for name in names:
            if overall_dict[name][day_index]:
                if overall_dict[name][day_index] < min:
                    min = overall_dict[name][day_index]
                    weight = weights[names.index(name)]
                elif overall_dict[name][day_index] == min:
                    weight = 0
        daily_weights.append(weight)
    datetimes = [dt.datetime(int(date.split('/')[2]),int(date.split('/')[0]), int(date.split('/')[1])) for date in dates]
    series = pd.Series(data=daily_weights, index=datetimes)
    cmap = matplotlib.colors.ListedColormap(['grey', 'skyblue', 'navajowhite', 'palegreen', 'lightcoral', 'plum'])
    fig, ax = calmap.calendarplot(series, fillcolor='silver', cmap=cmap, fig_kws=dict(figsize=(17,8)))
    labels = ['Tie'] + names
    formatter = plt.FuncFormatter(lambda val, loc: labels[int(val)])
    fig.colorbar(ax[0].get_children()[1], ax=ax.ravel().tolist(), shrink=0.4, format=formatter)
    plt.savefig(filename, dpi=500)
