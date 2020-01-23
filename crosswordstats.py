import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import time
import datetime as dt


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