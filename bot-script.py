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
from pytz import timezone
import pytz
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, PicklePersistence
import requests
from uuid import uuid4
import re
import copy
from telegram import ParseMode
from gtts import gTTS
from datetime import datetime, time, timedelta
from crosswordstats import lineplot, avgtimes
import os

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


def reset(update, context):
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
    msg = update.message.text.split()
    index = int(msg[1]) - 1
    for i in range(2, len(msg)):
        nameTime = msg[i].partition('-')
        name = nameTime[0]
        time = int(nameTime[2])
        context.chat_data['overall'][name].insert(index, time)


def testVar(update, context):
    update.message.reply_text(str(globalChatData))


def stats(update, context):
    topStr = update.message.text.partition(' ')[2]
    top = None
    if len(topStr) > 0:
        top = int(topStr)
    lineplot(context.chat_data['overall'], context.chat_data['overallDates'], 'overallLinePlot.png', ylim=top)
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open('overallLinePlot.png', 'rb'))
    os.remove('overallLinePlot.png')


def averages(update, context):
    avgtimes(context.chat_data['overall'], context.chat_data['overallDates'], 'avgBars.png')
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open('avgBars.png', 'rb'))
    os.remove('avgBars.png')


def addtime_msg(update, context):
    name = str(update.message.from_user.first_name)
    value = (update.message.text.partition(':'))
    if len(value[2]) != 0 & value[0].isdigit() & value[2].isdigit():
        first = value[0]
        if len(first) == 0:
            first = "0"
        second = value[2]
        total = 60 * int(first) + int(second)
        # Compare to min time for today and overall
        tz = timezone('EST')
        today = datetime.now(tz)
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
    key = str(update.message.from_user.first_name)
    time = context.chat_data['daily'][key]
    if key in context.chat_data['daily']:
        update.message.reply_text(time_to_string(time))
    else:
        update.message.reply_text("No recorded time found for " + key)


def dailytimes_manual(update, context):
    dailytimes_job(context)


def removeLastDate(update, context):
    context.chat_data['overallDates'].pop()


def removeLastTime(update, context):
    for name in context.chat_data['overall']:
        context.chat_data['overall'][name].pop()


def dailytimes_job(context):
    global globalChatData
    for chatID in globalChatData:
        rank = []
        dailyTimes = globalChatData[chatID]['daily']
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
            context.bot.send_message(chatID, "Day passed with no recorded times")
        else:
            mg = "Final Rankings for Today:"
            for i in range(len(rank)):
                time = dailyTimes[rank[i][0]]
                place = i + 1
                for name in rank[i]:
                    mg = mg + "\n" + str(place) + " " + name + " - " + time_to_string(time) + " "
            if len(rank[0]) == 1:
                mg += "\n" + rank[0][0] + " won!"
            elif len(rank[0]) == 2:
                mg += "\n" + rank[0][0] + " and " + rank[0][1] + " won!"
            else:
                mg += "\n"
                for j in range(len(rank[i] - 1)):
                    mg += rank[0][j] + ", "
                mg += "and " + rank[0][len(rank[0]) - 1] + " won!"
            context.bot.send_message(chatID, mg)
            for name in rank[0]:
                if not (name in globalChatData[chatID]['leaderboard']):
                    globalChatData[chatID]['leaderboard'][name] = 1
                else:
                    globalChatData[chatID]['leaderboard'][name] += 1
            totalRank = []
            for name in globalChatData[chatID]['leaderboard']:
                if len(totalRank) == 0:
                    totalRank.append([name])
                else:
                    i = 0
                    inserted = False
                    while i < len(totalRank) and not (inserted):
                        if globalChatData[chatID]['leaderboard'][name] > globalChatData[chatID]['leaderboard'][
                            totalRank[i][0]]:
                            totalRank.insert(i, [name])
                            inserted = True
                        elif globalChatData[chatID]['leaderboard'][name] == globalChatData[chatID]['leaderboard'][
                            totalRank[i][0]]:
                            totalRank[i].append(name)
                            inserted = True
                        else:
                            i += 1
                    if not (inserted):
                        totalRank.append([name])
            mg = "Overall Standings:"
            for i in range(len(totalRank)):
                for j in range(len(totalRank[i])):
                    name = totalRank[i][j]
                    place = i + 1
                    mg += "\n" + str(place) + " " + name + " - " + str(
                        globalChatData[chatID]['leaderboard'][name]) + " "
            context.bot.send_message(chatID, mg)
            for name in globalChatData[chatID]['overall']:
                globalChatData[chatID]['overall'][name].append(None)
            tz = timezone('EST')
            tomorrow = datetime.now(tz) + timedelta(days=1)
            globalChatData[chatID]['overallDates'].append(f'{tomorrow.month}/{tomorrow.day}/{tomorrow.year}')
            globalChatData[chatID]['daily'].clear()
            context.bot.unpinChatMessage(chatID)


def currentstandings(update, context):
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
        update.message.reply_text("No recorded times found for today")
    else:
        mg = "Today's Rankings: "
        for i in range(len(rank)):
            time = dailyTimes[rank[i][0]]
            seconds = "" + str(time % 60)
            if time % 60 < 10:
                seconds = "0" + seconds
            place = i + 1
            for name in rank[i]:
                mg = mg + "\n<b>" + str(place) + "</b> " + name + " - " + str(int(time / 60)) + ":" + seconds + " "
        if len(context.chat_data['daily']) == 1 or not ('pinnedStandings' in context.chat_data):
            context.chat_data['pinnedStandings'] = context.bot.send_message(update.message.chat_id, mg,
                                                                            parse_mode=ParseMode.HTML)
            context.bot.pinChatMessage(update.message.chat_id, context.chat_data['pinnedStandings'].message_id, True)
        else:
            context.bot.edit_message_text(mg, chat_id=update.message.chat_id,
                                          message_id=context.chat_data['pinnedStandings'].message_id,
                                          parse_mode=ParseMode.HTML)


def currentstandings_manual(update, context):
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
        for i in range(len(rank)):
            time = dailyTimes[rank[i][0]]
            seconds = "" + str(time % 60)
            if time % 60 < 10:
                seconds = "0" + seconds
            place = i + 1
            for name in rank[i]:
                mg = mg + "\n" + str(place) + " " + name + " - " + str(int(time / 60)) + ":" + seconds + " "
        update.message.reply_text(mg, parse_mode=ParseMode.HTML)


def leaderboard(update, context):
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
    audio.save("leaderboard.ogg")
    context.bot.send_voice(chat_id=doobieID, voice=open('leaderboard.ogg', 'rb'))
    os.remove("leaderboard.ogg")


def remind(context):
    context.bot.send_message(doobieID, "End of Crossword Day! Use /endday")


def insultmax(update, context):
    insults = ["Max sux", "Max is a doodee poopoo head", "Ew", "Did someone just fart? Oh nevermind, it was Max",
               "Max sucks at crossword", "Max is a poop poop poopy poop poop doodoodoodoodoodoodoo fart."]
    if str(update.message.from_user.first_name) == "Max":
        mg = "Wow great job entering that command there Max. I know that was you and not someone else. I'm not stupid, like you. ***REMOVED*** you."
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
        context.bot.send_message(chatID, str(globalChatData[chatID]))

def minTimes(update, context):
    name = str(update.message.from_user.first_name)
    mg = f'Best times for {name}:'
    for day in context.chat_data['minTimes'][name]:
        mg += f'\n{day} - {time_to_string(context.chat_data["minTimes"][name][day])}'
    update.message.reply_text(mg)

def time_to_string(time):
    seconds = "" + str(time % 60)
    if time % 60 < 10:
        seconds = "0" + seconds
    return str(int(time / 60)) + ":" + seconds

def testTimezone(context):
    for chatID in globalChatData:
        context.bot.send_message(chatID, 'Test: If it is 10 PM Eastern right now, then using timezones worked. '
                                         'Otherwise, whoopsies!')

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
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("removeLastDate", removeLastDate))
    dp.add_handler(CommandHandler("removeLastTime", removeLastTime))
    dp.add_handler(CommandHandler("averages", averages))
    dp.add_handler(CommandHandler("debugtime", debugtime))
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
    # EST: 6 PM. UTC: 11 PM.
    t6 = time(23, 0, 0, 0)
    testTime = time(3, 0, 0, 0, timezone('EST'))
    everyday = tuple(range(7))
    # Job at 10 PM EST Mon - Fri
    ten_pm_days = j.run_daily(dailytimes_job, t10, tenDays)
    # Job at 6 PM EST Sat & Sun
    six_pm_days = j.run_daily(dailytimes_job, t6, sixDays)
    test_job = j.run_daily(testTimezone, testTime, everyday)
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
