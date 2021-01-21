# CrosswordLeaderboardBot
A Telegram bot designed to record a groupchat's times for the New York Times Daily Mini Crossword.

# Functionality

## Basic Use
- Every day users can send their crossword time in their groupchat (e.g. 1:30) and the bot will record it in the groupchat's daily leaderboard. 
- Every day when a new crossword is available, the bot will update the groups All-Time leaderboard based on who had the lowest time for the previous day.

## Reminders 🔔
If a user in the groupchat doesn't submit a time within one hour of the next crossword day (10 pm EST as per the NYT app), the bot will DM them a friendly reminder, which they can choose to opt out of.

## Streaks 🔥
If a user is on a hotstreak and has won multiple days in a row, the bot will let them know!

## Crossword Stats 📈
The bot has 20(!) different commands for visualizing the group's recorded crossword data. Most of these are created using matplotlib and sent as images to the groupchat.

Some that are available:
### Calendar
Displays the winning user for each day. (usage: /calendar)

![Calendar](/images/calendar.jpg)

### Violin Plot
Shows the distribution of each user's submitted times. Seperates Saturdays from weekdays because Saturday puzzles are larger (midis). (usage: /violin)

![Violin](/images/violin.jpg)

### Best Fit Plot
Plots the best fit curve for a given user to a given degree. Good for seeing trends in crossword performance. (usage: /stats_best_fit [Name] [Degree])

![BestFit](/images/best_fit.jpg)

### Percentage Plot
Plots the percent of total wins each user has over time. Good for seeing trends in users' competing hold over their place in the leaderboard. (usage: /percentages)

![Percentages](/images/percentages.jpg)



*Note that I am not as good at crosswords as my amazing friends in these images*
