# homework-telegram-bot
##About
Simple API for creating an easy-to-use telegram bot, which sending:

- Homework for today
- Homework for tomorrow
- Homework on a particular subject
- Upcoming Events
- Weather forecast

##Installation
Requires:

- Python3
- PyTelegramBotAPI
- sqlite3

Download the bot:
`https://github.com/ARQtty/homework-telegram-bot.git`
(or download the [.zip](https://github.com/ARQtty/homework-telegram-bot/archive/master.zip))

First run:

`python3 homework-telegram-bot-master/createSchoolDB.py`

`python3 homework-telegram-bot-master/schoolBot.py`

##Functions

####In bot:

- /addhomework - add HW for any subject
- /weather - send actual weather for all users
- /addevent - add new event
- /noHW - erase homework for any subjects
- /getlog - bot sends temporary log

##Examples

![Example1](https://github.com/ARQtty/homework-telegram-bot/raw/master/src/p1.png "")
![Example2](https://github.com/ARQtty/homework-telegram-bot/raw/master/src/p2.png "")
