#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import datetime
import random
import statistics

from pytz import timezone
import pytz
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, PicklePersistence
import requests
from uuid import uuid4
import re
import copy
from telegram import ParseMode, Sticker
from gtts import gTTS
from datetime import datetime, time, timedelta
from crosswordstats import lineplot, avgtimes, lineplot_best, lineplot_best_fit, calendar_plot, lineplot_best_fit_week, \
    pie_plot, pie_time_plot, total_wins_plot, total_time_plot, best_times, violin_plot, swarm_plot, rankings_plot, \
    percentage_plot

import os
from collections import Counter
import csv
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

robertID = ***REMOVED***
# doobieID = 's1392971649'
doobieID = ***REMOVED***
globalChatData = dict()


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    if update.message.chat_id == doobieID:
        """Send a message when the command /start is issued."""
        if not ("leaderboard" in context.chat_data):
            context.chat_data["leaderboard"] = {}
            context.chat_data["daily"] = {}
            update.message.reply_text('New leaderboard and daily time started')
        else:
            update.message.reply_text('Leaderboard and daily time already defined!')
        if 'pinnedStandings' in context.chat_data:
            del context.chat_data['pinnedStandings']
            update.message.reply_text('Deleted pinned message from data')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s". Chat data: %s', update, context.error, context.chat_data)
    context.bot.send_message(doobieID, str(context.error))


def reset(update, context):
    if update.message.chat_id == doobieID:
        mg = update.message.text.partition(' ')[2].partition(' ')
        name = mg[0]
        num = mg[2]
        if not ('leaderboard' in context.chat_data):
            context.chat_data['leaderboard'] = dict()
        if int(num) == 0 and name in context.chat_data['leaderboard']:
            del context.chat_data['leaderboard'][name]
            update.message.reply_text(name + " deleted from leaderboard")
        elif int(num) > 0:
            context.chat_data['leaderboard'][name] = int(num)
            update.message.reply_text(name + " reset to " + num + " in leaderboard")


def initoverall(update, context):
    if update.message.chat_id == doobieID:
        if 'overall' not in context.chat_data or update.message.text.partition(' ')[2] == 'override':
            context.chat_data['overall'] = dict()
            context.chat_data['overall']['Max'] = [30, 559, 24, 70, 39, 26, 16, 30, 15, 33, 65, 22, 29, 38, 43, 16, 23, 29,
                                                   32, 24, 23, 50, 31, 23]
            context.chat_data['overall']['Macey'] = [None, 34, 40, None, 35, 60, 33, 37, 35, 49, 65, 27, None, 19, 44, 21,
                                                     48, 48, 30, 33, 25, 38, 36, 56]
            context.chat_data['overall']['Asher'] = [71, 124, 40, None, 58, 99, 39, None, 33, 32, 85, 24, 40, 30, 39, 40,
                                                     None, 51, None, 23, 24, 69, 66, 80]
            context.chat_data['overall']['Robert'] = [192, 101, 36, None, 111, 62, 51, 225, 78, 251, 149, 42, 97, 53, 206,
                                                      32, 130, 72, 90, 43, 56, 263, 110, 312]
            context.chat_data['overall']['Levi'] = [None, 238, 180, None, 256, None, None, None, 54, 61, 116, None, 86, 69,
                                                    50, 50, None, None, 102, 36, 35, None, 192, 110]
            context.chat_data['overallDates'] = list()
            for i in range(1, 26):
                context.chat_data['overallDates'].append(f'1/{i}/2020')
            for name in context.chat_data['overall']:
                if name not in context.chat_data['daily']:
                    context.chat_data['overall'][name].append(None)
                else:
                    context.chat_data['overall'][name].append(context.chat_data['daily'][name])
        else:
            update.message.reply_text("Overall is already defined. Don't screw things up, doofus!")


def addtime(update, context):
    if update.message.chat_id == doobieID:
        key = str(update.message.from_user.first_name)
        value = (update.message.text.partition(' ')[2]).partition(':')
        if len(value[2]) == 0:
            if key == "Max":
                update.message.reply_text("Wow " + key + " you suck. Banned.")
                update.message.chat.kick_member(update.message.from_user.id)
            update.message.reply_text("Try including a time, dumbass.")
        else:
            first = value[0]
            if len(first) == 0:
                first = "0"
            second = value[2]
            total = 60 * int(first) + int(second)
            duplicate = False
            if key in context.chat_data['daily']:
                duplicate = context.chat_data['daily'][key] == total
            global globalChatData
            if not update.message.chat_id in globalChatData:
                globalChatData[update.message.chat_id] = context.chat_data
            context.chat_data['daily'][key] = total
            if not (duplicate):
                currentstandings(update, context)


def debugtime(update, context):
    if update.message.chat_id == doobieID:
        msg = update.message.text.split()
        index = int(msg[1]) - 1
        for i in range(2, len(msg)):
            nameTime = msg[i].partition('-')
            name = nameTime[0]
            time = int(nameTime[2])
            context.chat_data['overall'][name].insert(index, time)


def testVar(update, context):
    if update.message.chat_id == doobieID:
        update.message.reply_text(str(globalChatData))


def times(update, context):
    if update.message.chat_id == doobieID:
        topStr = context.args[0]
        daysBack = context.args[1]
        top = None
        if len(topStr) > 0:
            top = int(topStr)
        if len(daysBack) > 0:
            daysBack = int(daysBack)
        else:
            daysBack = None
        lineplot(context.chat_data['overall'], context.chat_data['overallDates'], 'overallLinePlot.png', ylim=top,
                 daysBack=daysBack)
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('overallLinePlot.png', 'rb'))
        os.remove('overallLinePlot.png')


def stats_best(update, context):
    if update.message.chat_id == doobieID:
        topStr = update.message.text.partition(' ')[2]
        top = None
        if len(topStr) > 0:
            top = int(topStr)
        lineplot_best(context.chat_data['overall'], context.chat_data['overallDates'], 'overallLinePlot.png', ylim=top)
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('overallLinePlot.png', 'rb'))
        os.remove('overallLinePlot.png')


def stats_best_fit(update, context):
    if update.message.chat_id == doobieID:
        name = context.args[0]
        degree = context.args[1]
        lineplot_best_fit(context.chat_data['overall'], context.chat_data['overallDates'], 'bestFitPlot.png', name,
                          int(degree))
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('bestFitPlot.png', 'rb'))
        os.remove('bestFitPlot.png')


def week_best_fit(update, context):
    if update.message.chat_id == doobieID:
        name = context.args[0]
        degree = context.args[1]
        lineplot_best_fit_week(context.chat_data['overall'], context.chat_data['overallDates'], 'bestFitPlotWeek.png', name,
                               int(degree))
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('bestFitPlotWeek.png', 'rb'))
        os.remove('bestFitPlotWeek.png')


def averages(update, context):
    if update.message.chat_id == doobieID:
        avgtimes(context.chat_data['overall'], context.chat_data['overallDates'], 'avgBars.png')
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('avgBars.png', 'rb'))
        os.remove('avgBars.png')


def calendar(update, context):
    if update.message.chat_id == doobieID:
        calendar_plot(context.chat_data['overall'], context.chat_data['overallDates'], 'calendar.png')
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('calendar.png', 'rb'))
        os.remove('calendar.png')


def addtime_msg(update, context):
    if update.message.chat_id == doobieID:
        name = str(update.message.from_user.first_name)
        value = (update.message.text.partition(':'))
        user_id = update.message.from_user.id
        if 'ids' not in context.chat_data:
            context.chat_data['ids'] = dict()
        if user_id not in context.chat_data['ids'].keys():
            context.chat_data['ids'][user_id] = dict()
            context.chat_data['ids'][user_id]['Remind'] = True
        context.chat_data['ids'][user_id]['Received'] = True
        if len(value[2]) != 0 & value[0].isdigit() & value[2].isdigit():
            first = value[0]
            if len(first) == 0:
                first = "0"
            second = value[2]
            total = 60 * int(first) + int(second)
            # Compare to min time for today and overall=
            if name == 'Max' and total == 26:
                update.message.reply_sticker(sticker=
                                             'CAACAgEAAxkBAAICJ15pj6hc7Nr4zNyJQT7camZOEgPUAAKGAAOkJocMxc_x7wE2OzwYBA')
            if 'minTimes' not in context.chat_data:
                context.chat_data['minTimes'] = dict()
            if name not in context.chat_data['minTimes']:
                context.chat_data['minTimes'][name] = dict()
            if 'overall' not in context.chat_data['minTimes'][name]:
                min_time = None
                i = 0
                while min_time is None and i < len(context.chat_data['overall'][name]):
                    min_time = context.chat_data['overall'][name][i]
                    i += 1
                if min_time is not None:
                    for current_time in context.chat_data['overall'][name]:
                        if current_time is not None and current_time < min_time:
                            min_time = current_time
                    context.chat_data['minTimes'][name]['overall'] = min_time
            # *** Min Times Region ***
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            today = context.chat_data['overallDates'][-1].split('/')
            day_index = datetime(int(today[2]), int(today[0]), int(today[1])).weekday()
            if days[day_index] not in context.chat_data['minTimes'][name]:
                # Get index of first day
                first_day = context.chat_data['overallDates'][0].split('/')
                first_day_index = datetime(int(first_day[2]), int(first_day[0]), int(first_day[1])).weekday()
                # Shift index so first day corresponds to 0
                start_index = day_index - first_day_index
                if start_index < 0:
                    start_index += 7
                min_time = None
                i = start_index
                while min_time is None and i < len(context.chat_data['overall'][name]):
                    min_time = context.chat_data['overall'][name][i]
                    i += 7
                if min_time is not None:
                    while i < len(context.chat_data['overall'][name]):
                        current_time = context.chat_data['overall'][name][i]
                        if current_time is not None and current_time < min_time:
                            min_time = current_time
                        i += 7
                    context.chat_data['minTimes'][name][days[day_index]] = min_time
            # Check if new best day and overall time
            if total < context.chat_data['minTimes'][name][days[day_index]]:
                best_time_for = days[day_index]
                time_diff = time_to_string(context.chat_data['minTimes'][name][days[day_index]] - total)
                best_time_for += f' (\u2193 {time_diff})'
                context.chat_data['minTimes'][name][days[day_index]] = total
                if total < context.chat_data['minTimes'][name]['overall']:
                    best_time_for += ' and overall'
                    time_diff = time_to_string(context.chat_data['minTimes'][name]['overall'] - total)
                    best_time_for += f' (\u2193 {time_diff})'
                    context.chat_data['minTimes'][name]['overall'] = total
                update.message.reply_text(f"New best {best_time_for} time for " + name + "!")
            duplicate = False
            # Mark as duplicate
            if name in context.chat_data['daily']:
                duplicate = context.chat_data['daily'][name] == total
                # Make min time none if it is being overwritten by newly sent time
                if not duplicate and days[day_index] in context.chat_data['minTimes'][name] and \
                        context.chat_data['daily'][name] == context.chat_data['minTimes'][name][days[day_index]]:
                    del context.chat_data['minTimes'][name][days[day_index]]
                    min_deleted = days[day_index]
                    if 'overall' in context.chat_data['minTimes'][name] and \
                            context.chat_data['daily'][name] == context.chat_data['minTimes'][name]['overall']:
                        del context.chat_data['minTimes'][name]['overall']
                        min_deleted += " and overall"
                    update.message.reply_text(f"Deleted best {min_deleted} time for {name}. Will be recalculated upon "
                                              f"next entry.")
            # Add time to end of overall list
            context.chat_data['overall'][name][-1] = total
            global globalChatData
            if update.message.chat_id not in globalChatData:
                globalChatData[update.message.chat_id] = context.chat_data
            context.chat_data['daily'][name] = total
            if not duplicate:
                currentstandings(update, context)


def mytime(update, context):
    if update.message.chat_id == doobieID:
        key = str(update.message.from_user.first_name)
        time = context.chat_data['daily'][key]
        if key in context.chat_data['daily']:
            update.message.reply_text(time_to_string(time))
        else:
            update.message.reply_text("No recorded time found for " + key)


def dailytimes_manual(update, context):
    if update.message.chat_id == doobieID:
        dailytimes_job(context)


def removeLastDate(update, context):
    if update.message.chat_id == doobieID:
        context.chat_data['overallDates'].pop()


def removeLastTime(update, context):
    if update.message.chat_id == doobieID:
        for name in context.chat_data['overall']:
            context.chat_data['overall'][name].pop()


def dailytimes_job(context):
    global globalChatData
    for chatID in globalChatData:
        if chatID == doobieID:
            rank = []
            dailyTimes = globalChatData[chatID]['daily']
            for name, time in dailyTimes.items():
                if len(rank) == 0:
                    rank.append([name])
                else:
                    # iterate rank to insert name
                    i = 0
                    inserted = False
                    while i < len(rank) and not inserted:
                        if time < dailyTimes[rank[i][0]]:
                            rank.insert(i, [name])
                            inserted = True
                        elif time == dailyTimes[rank[i][0]]:
                            rank[i].append(name)
                            inserted = True
                        else:
                            i += 1
                    if not (inserted):
                        rank.append([name])
            if len(rank) == 0:
                context.bot.send_message(chatID, "Day passed with no recorded times")
            else:
                mg = "Final Rankings for Today:"
                for i in range(len(rank)):
                    time = dailyTimes[rank[i][0]]
                    place = i + 1
                    for name in rank[i]:
                        mg = mg + "\n<b>" + str(place) + "</b> " + name + " - " + time_to_string(time) + " "
                if len(rank[0]) == 1:
                    mg += "\n" + rank[0][0] + " won!"
                elif len(rank[0]) == 2:
                    mg += "\n" + rank[0][0] + " and " + rank[0][1] + " won!"
                else:
                    mg += "\n"
                    for j in range(len(rank[0]) - 1):
                        mg += rank[0][j] + ", "
                    mg += "and " + rank[0][len(rank[0]) - 1] + " won!"
                context.bot.send_message(chatID, mg, parse_mode=ParseMode.HTML)
                win_statuses = []
                if 'streaks' not in globalChatData[chatID]:
                    globalChatData[chatID]['streaks'] = dict()
                if 'best_streak' not in globalChatData[chatID]:
                    globalChatData[chatID]['best_streak'] = 0
                for name in list(globalChatData[chatID]['streaks'].keys()):
                    if name not in rank[0]:
                        if globalChatData[chatID]['streaks'][name] > globalChatData[chatID]['best_streak']:
                            globalChatData[chatID]['best_streak'] = globalChatData[chatID]['streaks'][name]
                            context.bot.send_message(chatID, f'{name} ended the best streak on record - '
                                                             f'{globalChatData[chatID]["streaks"][name]} days!')
                        del globalChatData[chatID]['streaks'][name]
                for name in rank[0]:
                    if name not in globalChatData[chatID]['leaderboard']:
                        globalChatData[chatID]['leaderboard'][name] = 1
                    else:
                        globalChatData[chatID]['leaderboard'][name] += 1
                    status = emoji_status(globalChatData[chatID]['leaderboard'][name])
                    if status[2]:
                        win_statuses.append(f'{name} attained {status[0]} status!')
                    if name in globalChatData[chatID]['streaks']:
                        globalChatData[chatID]['streaks'][name] += 1
                        # Check for longest streak, change admin title
                        """if globalChatData[chatID]['streaks'][name] > globalChatData[chatID]['best_streak']:
                            if 'best_streak_name' not in globalChatData[chatID]:
                                globalChatData[chatID]['best_streak_name'] = name
                                admins = context.bot.get_chat_administrators(chatID)
                                admin_id = next((admin.user.id for admin in admins if admin.user.first_name == name), None)
                                if admin_id:
                                    context.bot.set
                            elif name != globalChatData[chatID]['best_streak_name']:
                                admins = context.bot.get_chat_administrators(chatID)
                                admin_id = next((admin.user.id for admin in admins if admin.user.first_name == name),
                                                None)
                                if admin_id:
                                    context.bot.set"""
                    else:
                        globalChatData[chatID]['streaks'][name] = 1
                total_rank = []
                for name in globalChatData[chatID]['leaderboard']:
                    if len(total_rank) == 0:
                        total_rank.append([name])
                    else:
                        i = 0
                        inserted = False
                        while i < len(total_rank) and not inserted:
                            if globalChatData[chatID]['leaderboard'][name] > \
                                    globalChatData[chatID]['leaderboard'][total_rank[i][0]]:
                                total_rank.insert(i, [name])
                                inserted = True
                            elif globalChatData[chatID]['leaderboard'][name] == \
                                    globalChatData[chatID]['leaderboard'][total_rank[i][0]]:
                                total_rank[i].append(name)
                                inserted = True
                            else:
                                i += 1
                        if not inserted:
                            total_rank.append([name])
                mg = "<b>Overall Standings:</b>"
                # Streak superscript
                sup = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
                x = 'ˣ'
                for i in range(len(total_rank)):
                    for j in range(len(total_rank[i])):
                        name = total_rank[i][j]
                        place = i + 1
                        streak = ''
                        if name in globalChatData[chatID]['streaks'] and globalChatData[chatID]['streaks'][name] > 1:
                            streak = str(globalChatData[chatID]['streaks'][name]).translate(sup)
                        mg += "\n<b>" + str(place) + "</b> " + name + streak + " - " + str(
                            globalChatData[chatID]['leaderboard'][name]) + " " + \
                              emoji_status(globalChatData[chatID]['leaderboard'][name])[1]
                for win_status in win_statuses:
                    mg += "\n" + win_status
                context.bot.send_message(chatID, mg, parse_mode=ParseMode.HTML)
                for name in globalChatData[chatID]['overall']:
                    globalChatData[chatID]['overall'][name].append(None)
                if 'ids' in globalChatData[chatID]:
                    for user_id in globalChatData[chatID]['ids']:
                        globalChatData[chatID]['ids'][user_id]['Received'] = False
                tz = timezone('EST')
                tomorrow = datetime.now(tz) + timedelta(days=1)
                globalChatData[chatID]['overallDates'].append(f'{tomorrow.month}/{tomorrow.day}/{tomorrow.year}')
                globalChatData[chatID]['daily'].clear()
                context.bot.unpinChatMessage(chatID)


def currentstandings(update, context):
    if update.message.chat_id == doobieID:
        rank = []
        dailyTimes = context.chat_data['daily']
        for name, time in dailyTimes.items():
            if len(rank) == 0:
                rank.append([name])
            else:
                # iterate rank to insert name
                i = 0
                inserted = False
                while i < len(rank) and not (inserted):
                    if time < dailyTimes[rank[i][0]]:
                        rank.insert(i, [name])
                        inserted = True
                    elif time == dailyTimes[rank[i][0]]:
                        rank[i].append(name)
                        inserted = True
                    else:
                        i += 1
                if not inserted:
                    rank.append([name])
        if len(rank) == 0:
            update.message.reply_text('No recorded times found for today')
        else:
            mg = "Today's Rankings: "
            sup = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
            x = 'ˣ'
            for i in range(len(rank)):
                time = dailyTimes[rank[i][0]]
                seconds = "" + str(time % 60)
                if time % 60 < 10:
                    seconds = "0" + seconds
                place = i + 1
                for name in rank[i]:
                    streak = ''
                    if 'streaks' in context.chat_data and name in context.chat_data['streaks']:
                        if place == 1:
                            streak = str(context.chat_data['streaks'][name] + 1).translate(sup)
                        elif context.chat_data['streaks'][name] > 1:
                            streak = str(context.chat_data['streaks'][name]).translate(sup)
                            streak = x + streak
                    mg = mg + "\n<b>" + str(place) + "</b> " + name + streak + " - " + str(int(time / 60)) + ":" + \
                         seconds + " "
            if len(context.chat_data['daily']) == 1 or not ('pinnedStandings' in context.chat_data):
                context.chat_data['pinnedStandings'] = context.bot.send_message(update.message.chat_id, mg,
                                                                                parse_mode=ParseMode.HTML)
                context.bot.pinChatMessage(update.message.chat_id, context.chat_data['pinnedStandings'].message_id, True)
            else:
                context.bot.edit_message_text(mg, chat_id=update.message.chat_id,
                                              message_id=context.chat_data['pinnedStandings'].message_id,
                                              parse_mode=ParseMode.HTML)


def currentstandings_manual(update, context):
    if update.message.chat_id == doobieID:
        rank = []
        dailyTimes = context.chat_data['daily']
        for name, time in dailyTimes.items():
            if len(rank) == 0:
                rank.append([name])
            else:
                # iterate rank to insert name
                i = 0
                inserted = False
                while i < len(rank) and not (inserted):
                    if time < dailyTimes[rank[i][0]]:
                        rank.insert(i, [name])
                        inserted = True
                    elif time == dailyTimes[rank[i][0]]:
                        rank[i].append(name)
                        inserted = True
                    else:
                        i += 1
                if not (inserted):
                    rank.append([name])
        if len(rank) == 0:
            update.message.reply_text("No recorded times found for today")
        else:
            mg = "Today's Rankings: "
            sup = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
            x = 'ˣ'
            for i in range(len(rank)):
                time = dailyTimes[rank[i][0]]
                seconds = "" + str(time % 60)
                if time % 60 < 10:
                    seconds = "0" + seconds
                place = i + 1
                for name in rank[i]:
                    streak = ''
                    if 'streaks' in context.chat_data and name in context.chat_data['streaks']:
                        if place == 1:
                            streak = str(context.chat_data['streaks'][name] + 1).translate(sup)
                        elif context.chat_data['streaks'][name] > 1:
                            streak = str(context.chat_data['streaks'][name] + 1).translate(sup)
                            streak = x + streak
                    mg = mg + "\n" + str(place) + " " + name + streak + " - " + str(int(time / 60)) + ":" + seconds + " "
            update.message.reply_text(mg, parse_mode=ParseMode.HTML)


def leaderboard(update, context):
    if update.message.chat_id == doobieID:
        totalRank = []
        for name in context.chat_data['leaderboard']:
            if len(totalRank) == 0:
                totalRank.append([name])
            else:
                i = 0
                inserted = False
                while i < len(totalRank) and not (inserted):
                    if context.chat_data['leaderboard'][name] > context.chat_data['leaderboard'][totalRank[i][0]]:
                        totalRank.insert(i, [name])
                        inserted = True
                    elif context.chat_data['leaderboard'][name] == context.chat_data['leaderboard'][totalRank[i][0]]:
                        totalRank[i].append(name)
                        inserted = True
                    else:
                        i += 1
                if not (inserted):
                    totalRank.append([name])
        """ mg = "Overall Standings:"
        for i in range(len(totalRank)):
            for j in range(len(totalRank[i])):
                name = totalRank[i][j]
                place = i + 1
                mg += "\n" + str(place) + " " + name + " - " + str(context.chat_data['leaderboard'][name]) + " "
        update.message.reply_text(mg)"""
        mg = "Here is the overall leaderboard. "
        places = ["first", "second", "third", "fourth", "fifth"]
        for i in range(len(totalRank)):
            if i != 0:
                mg += "Then, "
                mg += f"in {places[i]} place is "
            if len(totalRank[i]) == 1:
                mg += f"{totalRank[i][0]} "
            elif len(totalRank[i]) == 2:
                mg += f"{totalRank[i][0]} and {totalRank[i][1]} "
            else:
                for j in range(len(totalRank[i]) - 1):
                    mg += f"{totalRank[i][j]}, "
                mg += f"and {totalRank[i][len(totalRank[i]) - 1]} "
            points = context.chat_data['leaderboard'][totalRank[i][0]]
            mg += f"with {points} win"
            if points > 1:
                mg += "s"
            mg += ". "
        audio = gTTS(text=mg, lang='en', slow=False)
        gTTS()
        audio.save("leaderboard.ogg")
        context.bot.send_voice(chat_id=doobieID, voice=open('leaderboard.ogg', 'rb'))
        os.remove("leaderboard.ogg")


def insultmax(update, context):
    insults = ["Max sux", "Max is a doodee poopoo head", "Ew", "Did someone just fart? Oh nevermind, it was Max",
               "Max sucks at crossword", "Max is a poop poop poopy poop poop doodoodoodoodoodoodoo fart."]
    if str(update.message.from_user.first_name) == "Max":
        mg = "Wow great job entering that command there Max. I know that was you and not someone else. I'm not " \
             "stupid, like you. ***REMOVED*** you."
    else:
        mg = insults[random.randrange(5)]
    audio = gTTS(text=mg, lang='en', slow=False)
    audio.save("max.ogg")
    context.bot.send_voice(chat_id=doobieID, voice=open('max.ogg', 'rb'))
    os.remove("max.ogg")


def talk(update, context):
    mg = update.message.text.partition(' ')[2]
    audio = gTTS(text=mg, lang='en', slow=False)
    audio.save("talk.ogg")
    context.bot.send_voice(chat_id=doobieID, voice=open('talk.ogg', 'rb'))
    os.remove("talk.ogg")


def sendJob(context):
    context.bot.send_message(robertID, "Job sent")


def sendVar(update, context):
    global globalChatData
    for chatID in globalChatData:
        if chatID == doobieID:
            context.bot.send_message(chatID, str(globalChatData[chatID]))


def minTimes(update, context):
    if update.message.chat_id == doobieID:
        best_times(context.chat_data['minTimes'], 'best_times.png')
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('best_times.png', 'rb'))
        os.remove('best_times.png')


def time_to_string(time):
    seconds = "" + str(time % 60)
    if time % 60 < 10:
        seconds = "0" + seconds
    return str(int(time / 60)) + ":" + seconds


def testTimezone(context):
    for chatID in globalChatData:
        context.bot.send_message(chatID, 'Test: If it is 10 PM Eastern right now, then using timezones worked. '
                                         'Otherwise, whoopsies!')


def emoji_status(level):
    emojis = {1: ['Paper', '📝'], 2: ['Cotton', '🧺'], 3: ['Leather', '👞'], 4: ['Fruit', '🍎'], 5: ['Wood', '🌲'],
              6: ['Iron', '🗜'], 7: ['Wool', '🧤'], 8: ['Bronze', '🥉'], 9: ['Pottery', '🏺'], 10: ['Tin', '🥫'],
              11: ['Steel', '🍴'], 12: ['Silk', '👘'], 13: ['Lace', '🧶'], 14: ['Ivory', '🐘'], 15: ['Crystal', '🔮'],
              20: ['Porcelain', '🚽'], 25: ['Silver', '🥈'], 30: ['Pearl', '⚪️'], 35: ['Coral', '🐠'],
              40: ['Ruby', '♦️'], 45: ['Sapphire', '🔹'], 50: ['Gold', '🥇'], 55: ['Emerald', '🟩'],
              60: ['Yellow Diamond', '✨'], 65: ['Blue Sapphire', '🔷'], 70: ['Platinum', '💳'], 75: ['Diamond', '💎'],
              80: ['Oak', '🌳'], 85: ['Moonstone', '🌛'], 90: ['Granite', '🌑']}
    if level % 100 == 0:
        just_attained = True
        status = 'Hundred'
        emoji = (level // 100) * '💯'
    else:
        value = level % 100
        just_attained = value in emojis
        while value not in emojis:
            value -= 1
        status = emojis[value][0]
        emoji = ((level // 100) * '💯') + emojis[value][1]
    if level > 100:
        status += ' ' + (((level // 100) + 1) * 'I')
    return [status, emoji, just_attained]


def dm_test(update, context):
    user_id = update.message.from_user.id
    context.bot.send_message(user_id, 'Hey cutie')


def remind(context):
    for chatID in globalChatData:
        if 'ids' in globalChatData[chatID]:
            for user_id in globalChatData[chatID]['ids']:
                if not globalChatData[chatID]['ids'][user_id]['Received'] and globalChatData[chatID]['ids'][user_id]['Remind']:
                    context.bot.send_message(user_id, "Reminder: You have one hour to submit your crossword time! Use "
                                                      "/stop_reminders to stop getting this reminder.")


def stop_reminders(update, context):
    global globalChatData
    user_id = update.message.from_user.id
    for chatID in globalChatData:
        if 'ids' in globalChatData[chatID] and user_id in globalChatData[chatID]['ids']:
            if globalChatData[chatID]['ids'][user_id]['Remind']:
                globalChatData[chatID]['ids'][user_id]['Remind'] = False
                context.bot.send_message(user_id, 'Stopping reminders. Use /send_reminders if you change your mind.')
            else:
                context.bot.send_message(user_id, 'Reminders are already inactive!')


def send_reminders(update, context):
    global globalChatData
    user_id = update.message.from_user.id
    for chatID in globalChatData:
        if 'ids' in globalChatData[chatID] and user_id in globalChatData[chatID]['ids']:
            if not globalChatData[chatID]['ids'][user_id]['Remind']:
                globalChatData[chatID]['ids'][user_id]['Remind'] = True
                context.bot.send_message(user_id, 'Now sending reminders.')
            else:
                context.bot.send_message(user_id, 'Reminders are already active!')


def reset_streak(update, context):
    if update.message.chat_id == doobieID:
        initial_value = context.chat_data['streaks'][context.args[0]]
        context.chat_data['streaks'][context.args[0]] = int(context.args[1])
        update.message.reply_text(
            f"{context.args[0]}'s streak reset from {initial_value} to {context.chat_data['streaks'][context.args[0]]}")


def pie(update, context):
    if update.message.chat_id == doobieID:
        pie_plot(context.chat_data['leaderboard'], 'pie.png')
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('pie.png', 'rb'))
        os.remove('pie.png')


def pie_gif(update, context):
    if update.message.chat_id == doobieID:
        pie_time_plot(context.chat_data['overall'], context.chat_data['overallDates'], 'pie.gif')
        context.bot.send_animation(chat_id=update.message.chat_id, animation=open('pie.gif', 'rb'))
        os.remove('pie.gif')


def total(update, context):
    if update.message.chat_id == doobieID:
        total_wins_plot(context.chat_data['overall'], context.chat_data['overallDates'], 'total.png')
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('total.png', 'rb'))
        os.remove('total.png')


def month_total(update, context):
    if update.message.chat_id == doobieID:
        total_wins_plot(context.chat_data['overall'], context.chat_data['overallDates'], 'total.png', past_month=True)
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('total.png', 'rb'))
        os.remove('total.png')


def total_time(update, context):
    if update.message.chat_id == doobieID:
        total_time_plot(context.chat_data['overall'], context.chat_data['overallDates'], 'total_time.png')
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('total_time.png', 'rb'))
        os.remove('total_time.png')


def month_total_time(update, context):
    if update.message.chat_id == doobieID:
        total_time_plot(context.chat_data['overall'], context.chat_data['overallDates'], 'total_time.png',
                        past_month=True)
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('total_time.png', 'rb'))
        os.remove('total_time.png')

def violin(update, context):
    if update.message.chat_id == doobieID:
        violin_plot(context.chat_data['overall'], context.chat_data['overallDates'], 'violin.png')
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('violin.png', 'rb'))
        os.remove('violin.png')


def swarm(update, context):
    if update.message.chat_id == doobieID:
        swarm_plot(context.chat_data['overall'], context.chat_data['overallDates'], 'swarm.png')
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('swarm.png', 'rb'))
        os.remove('swarm.png')


def stats(update, context):
    command = update.message.text.split()
    if len(command) > 1 and command[1] in context.chat_data['overall']:
        name = command[1]
    else:
        name = str(update.message.from_user.first_name)
    user_times = [t for t in context.chat_data['overall'][name] if t is not None]
    sum_time = str(timedelta(seconds=sum(user_times)))
    mean = statistics.mean(user_times)
    median = statistics.median(user_times)
    commonality = Counter(user_times).most_common()
    max_count = commonality[0][1]
    modes = [str(item[0]) for item in commonality if item[1] == max_count]
    variance = round(statistics.pvariance(user_times, mean), 2)
    stdev = round(statistics.pstdev(user_times, mean), 2)
    mean = round(mean, 2)

    message = f'<b>Stats for {name}:</b>\n' \
              f'Total: {sum_time}\n'\
              f'Mean: {mean} sec\n' \
              f'Median: {median} sec\n' \
              f'Mode: {", ".join(modes)} sec ({max_count} times)\n' \
              f'Variance: {variance} sec²\n' \
              f'Standard Deviation: {stdev} sec'

    update.message.reply_text(message, parse_mode=ParseMode.HTML)


def rankings(update, context):
    if update.message.chat_id == doobieID:
        ranks = rankings_plot(context.chat_data['overall'], context.chat_data['overallDates'], 'rankings.png')
        mg = '<b>Ranked Rankings:</b>\n'
        for i, name in enumerate(sorted(ranks.keys(), key=ranks.get, reverse=True)):
            mg += f'<b>{i+1}</b> {name}: {ranks[name]}\n'
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('rankings.png', 'rb'))
        context.bot.send_message(update.message.chat_id, mg, parse_mode=ParseMode.HTML)
        os.remove('rankings.png')

def month_rankings(update, context):
    if update.message.chat_id == doobieID:
        ranks = rankings_plot(context.chat_data['overall'], context.chat_data['overallDates'], 'rankings.png',
                              past_month=True)

        # Get month name for output message
        lds = [int(s) for s in context.chat_data['overallDates'][-1].split('/')]
        last_date = datetime(year=int(lds[2]), month=int(lds[0]), day=int(lds[1]))
        # Gets month name
        month = last_date.strftime("%B")
        mg = f'<b>Ranked Rankings for {month}:</b>\n'

        for i, name in enumerate(sorted(ranks.keys(), key=ranks.get, reverse=True)):
            mg += f'<b>{i+1}</b> {name}: {ranks[name]}\n'
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('rankings.png', 'rb'))
        context.bot.send_message(update.message.chat_id, mg, parse_mode=ParseMode.HTML)
        os.remove('rankings.png')


def percentages(update, context):
    if update.message.chat_id == doobieID:
        percentage_plot(context.chat_data['overall'], context.chat_data['overallDates'], 'percentages.png')
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('percentages.png', 'rb'))
        os.remove('percentages.png')


def get_day(update, context):
    if update.message.chat_id == doobieID or update.message.from_user.id == robertID:
        date = update.message.text.split()[1]
        message = ''
        global globalChatData
        if date in globalChatData[doobieID]['overallDates']:
            i = context.chat_data['overallDates'].index(date)
            for user in context.chat_data['overall']:
                time = context.chat_data['overall'][user][i]
                message += f'{user} - {time_to_string(time)}\n'
        else:
            message = f'Date {date} not found'
        context.bot.send_message(message)

def set_day(update, context):
    if update.message.from_user.id == robertID:
        date = update.message.text.split()[1]
        lines = update.message.text.splitlines()
        update.message.bot.send_message(str(lines))
        global globalChatData
        if date in globalChatData[doobieID]['overallDates']:
            message = 'todo'
        else:
            message = f'Date {date} already in list'
        context.bot.send_message(message)

def override_day(update, context):
    if update.message.from_user.id == robertID:
        date = update.message.text.split()[1]
        lines = update.message.text.splitlines()
        update.message.bot.send_message(str(lines))
        global globalChatData
        if date in globalChatData[doobieID]['overallDates']:
            message = 'todo'
        else:
            message = f'Date {date} already in list'
        context.bot.send_message(message)

def write_csv(update, context):
    if update.message.from_user.id == doobieID or update.message.from_user.id == robertID:
        chat_data = globalChatData[doobieID]
        names = [name for name in chat_data['overall']]
        header = ['Date'] + names
        with open('crossword_times.csv', 'w') as fp:
            writer = csv.writer(fp, delimiter=',')
            writer.writerow(header)
            for i in range(len(chat_data['overallDates'])):
                row = [chat_data['overallDates'][i]]
                for name in names:
                    row.append(chat_data['overall'][name][i])
                writer.writerow(row)
        context.bot.send_document(doobieID, document=open('crossword_time.csv', 'rb'))


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    botPersistence = PicklePersistence(filename='bot-data')
    updater = Updater(***REMOVED***, persistence=botPersistence, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("addtime", addtime))
    dp.add_handler(CommandHandler("mytime", mytime))
    dp.add_handler(CommandHandler("insultmax", insultmax))
    dp.add_handler(CommandHandler("today", currentstandings_manual))
    dp.add_handler(CommandHandler("endday", dailytimes_manual))
    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(CommandHandler("talk", talk))
    dp.add_handler(CommandHandler("leaderboard", leaderboard))
    dp.add_handler(MessageHandler(Filters.regex(r'^[\d]*:[\d]{2}$'), addtime_msg))
    dp.add_handler(CommandHandler("sendVar", sendVar))
    dp.add_handler(CommandHandler("initoverall", initoverall))
    dp.add_handler(CommandHandler("times", times))
    dp.add_handler(CommandHandler("stats_best", stats_best))
    dp.add_handler(CommandHandler("removeLastDate", removeLastDate))
    dp.add_handler(CommandHandler("removeLastTime", removeLastTime))
    dp.add_handler(CommandHandler("averages", averages))
    dp.add_handler(CommandHandler("debugtime", debugtime))
    dp.add_handler(CommandHandler("best", minTimes))
    dp.add_handler(CommandHandler("dm_me", dm_test))
    dp.add_handler(CommandHandler("stop_reminders", stop_reminders))
    dp.add_handler(CommandHandler("send_reminders", send_reminders))
    dp.add_handler(CommandHandler("reset_streak", reset_streak))
    dp.add_handler(CommandHandler("stats_best_fit", stats_best_fit))
    dp.add_handler(CommandHandler("week_best_fit", week_best_fit))
    dp.add_handler(CommandHandler("calendar", calendar))
    dp.add_handler(CommandHandler("pie", pie))
    dp.add_handler(CommandHandler("pie_gif", pie_gif))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("total", total))
    dp.add_handler(CommandHandler("month_total", month_total))
    dp.add_handler(CommandHandler("total_time", total_time))
    dp.add_handler(CommandHandler("month_total_time", month_total_time))
    dp.add_handler(CommandHandler("violin", violin))
    dp.add_handler(CommandHandler("swarm", swarm))
    dp.add_handler(CommandHandler("rankings", rankings))
    dp.add_handler(CommandHandler("month_rankings", month_rankings))
    dp.add_handler(CommandHandler("percentages", percentages))
    dp.add_handler(CommandHandler("get_day", get_day))
    dp.add_handler(CommandHandler("set_day", set_day))
    dp.add_handler(CommandHandler("override_day", override_day))
    dp.add_handler(CommandHandler("write_csv", write_csv))
    # on noncommand i.e message - echo the message on Telegram
    # log all errors
    dp.add_error_handler(error)
    j = updater.job_queue
    # EST: Monday - Friday. UTC: Tuesday - Saturday
    tenDays = (1, 2, 3, 4, 5)
    # EST & UTC: Satuday and Sunday
    sixDays = (5, 6)
    # EST: 10 PM. UTC: 3 AM.
    t10 = time(3, 0, 0, 0)
    t9 = time(2, 0, 0, 0)
    # EST: 6 PM. UTC: 11 PM.
    t6 = time(23, 0, 0, 0)
    t5 = time(22, 0, 0, 0)
    # Job at 10 PM EST Mon - Fri
    ten_pm_days = j.run_daily(dailytimes_job, t10, tenDays)
    remind_9_pm = j.run_daily(remind, t9, tenDays)
    # Job at 6 PM EST Sat & Sun
    six_pm_days = j.run_daily(dailytimes_job, t6, sixDays)
    remind_9_pm = j.run_daily(remind, t5, sixDays)
    # repeat = j.run_repeating(sendJob, interval=5, first = 0)
    # Start the Bot
    # j.start()
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
