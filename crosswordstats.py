import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import time
import datetime as dt
import pandas as pd

def lineplot(overall_dict, dates, filename, ylim=None):
    fig, ax = plt.subplots()
    x = [dt.datetime.strptime(d, '%m/%d/%Y').date() for d in dates]
    for name in overall_dict:
        plt.plot(x, overall_dict[name], 'o-', label=name, ms=3)
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

def lineplot_best(overall_dict, dates, filename, ylim=None):
    fig, ax = plt.subplots()
    x = [dt.datetime.strptime(d, '%m/%d/%Y').date() for d in dates]

    x_non = []
    x_sat = []
    best_non = []
    best_sat = []
    for name in overall_dict:
        for i in range(len(overall_dict[name])):
            x_curr, best_curr = x_sat, best_sat if i % 7 == 3 else x_non, best_non
            x_curr.append(x[i])
            if len(best) < len(overall_dict[name]):
                best_curr.append(overall_dict[name][i])
            elif overall_dict[name][i] != None and best[i] > overall_dict[name][i]:
                best_curr[i] = overall_dict[name][i]
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
