import sqlite3
import datetime as dt
import random
from time import sleep

import telebot 	# pyTelegramBotAPI

import weatherQuery as weather

'''
Commands (for bot's administrator):

/addhomework - add HW for any subject
/weather - send actual weather for all users in rss_list table (goto inBase())
/addevent - add new event
/noHW - erase homework for any subjects
/getlog - bot sends log
'''

token = '12345'
admins_id_list = [000000000]
log_path = 'homework-telegram-bot/'
bot = telebot.TeleBot(token)
markup = telebot.types.ReplyKeyboardMarkup()
subjectsList = ['Chemistry', 'Physics', 'etc']
weekdayDict = {0: 'monday', 1: 'tuesday', 'etc':'', 6: 'sunday'}
point = '\U000025AA'
succes = '\U00002705'

markup.row("What's tomorrow?")
markup.row('Events', 'Info')
markup.row('Chemistry', 'Physics')
markup.row('etc')
markup.row("What's today?")


#[[message text], writeToLog, bot's answer]
customMessages = [[['❤', '💙'],'send a ❤','Love u too ❤'],
                  [['thanks','thnx','thank u'],'thank me', "Don't mention it!"]]

# [[message text], writeToLog, bot's answer, nameOfSticer]
customStickerMessages = [[['chiken'],'greben','','greben']]


def logger(log_message, operation):
    with open(log_path + 'log.txt', 'a') as log:
        now = str(dt.datetime.now())[0:19]
        log.write(now + ' - ' + log_message.from_user.first_name + ' - ' + operation + '\n')


def sqlAcces(func):
	# Used as decorator
    conn = sqlite3.connect('homework-telegram-bot-master/subjects.sqlite')
    cursor = conn.cursor()
    func(conn, cursor)    # conn for commits and cursor
    cursor.close()
    conn.close()


def inBase(message):
	# Check user's location in chat_ids table
    @sqlAcces
    def inbase(conn, cursor):
        cursor.execute('SELECT * FROM rss_list')    # chat_ids
        row = cursor.fetchone()
        users = []
        while row is not None:
                users.append(row[1])
                row = cursor.fetchone()
        if users.count(message.from_user.first_name) == 0:
            cursor.execute('INSERT INTO rss_list (chat_id, Username) VALUES (?, ?)', (message.chat.id, message.from_user.first_name))
            logger(message, 'added %s to rss_list' % message.from_user.first_name)
        conn.commit()
        return 0


def tomorrowDate():
    # Returns yyyy-mm-dd
    today = dt.date.today()
    tomorrow = str(today + dt.timedelta(days=1))
    return tomorrow


def todayHomework(message):
	# Response for todayHW query
    if defineWeekdayByDate(tomorrowDate()) == 'monday':
        bot.send_message(message.chat.id, "Today's Sunday! None not a sadist asks ds on Sunday (and tomorrow - is even ask)")
        return 1
    @sqlAcces
    def returnTdHW(conn, cursor):
    	# Extract all homework for today
        cursor.execute('SELECT * FROM subjects WHERE dateToExec=?', (dt.date.today(), ))
        row = cursor.fetchone()
        response = ''
        if row is None:    # If no HW
            response = 'No homework)'
        else:
            while row is not None:
                response += '%s %s - %s\n' % (point, row[0], row[3]) # subject - homework
                row = cursor.fetchone()
        bot.send_message(message.chat.id, response, reply_markup=None) # Send full HW
        return 1


def end(date):
	# Into: mm-dd (01-15, 02-01, 02-4)
	# !!! make months
	date = date.replace('0', '')
	date = date.split('-')
	if date[0] == '1':
		mounth = 'January'
	elif date[0] == '2':
		mounth = 'February'
	return 'for ' + date[1] + 'th of ' + mounth


def tomorrowHomework(message):
	# Response for tomorrowHW query
    if defineWeekdayByDate(tomorrowDate()) == 'sunday':
        bot.send_message(message.chat.id, "Tomorrow is Sunday! What are you, who does ds Saturday?! Excellent what?!")
        return 1
    @sqlAcces
    def returnTwHW(conn, cursor):
        # Creating HW message
        cursor.execute('SELECT * FROM subjects WHERE dateToExec=?', (tomorrowDate(), ))    # Извлечь все ДЗ на завтра
        row = cursor.fetchone()
        response = ''
        if row is None:
            response = 'No homework)'
        else:
            while row is not None:
                response += '%s %s - %s\n' % (point, row[0], row[3])
                row = cursor.fetchone()

        # Create Events message
        response += '\n'
        cursor.execute('SELECT * FROM events WHERE deadline=?', (tomorrowDate(), ))
        row = cursor.fetchone()
        if row is None:
            pass
        else:
            while row is not None:
                response += point + row[0] + '\n'
                row = cursor.fetchone()

        bot.send_message(message.chat.id, response, reply_markup=None) # Send all
        return 1


def currentSubject(message):
	# Response for messages kinda 'Physics','Chemistry'
    @sqlAcces
    def getCrntSbj(conn, cursor):
        cursor.execute('SELECT * FROM subjects WHERE SubjName=?', (message.text, ))
        homework = cursor.fetchone()
        print(homework[3])
        if homework[3].lower() == 'no homework':
            bot.send_message(message.chat.id, 'There is no homework for this subject')
        else:
            bot.send_message(message.chat.id, '%s - "%s" %s (%s)' % (message.text, homework[3], end(homework[2][6:]), homework[1]), reply_markup=None)
        return 1


def defineWeekdayByDate(date):
    # input: mm-dd or yyyy-mm-dd
    if date[:4] == '2017':
        mm = date.split('-')[1]
        dd = date.split('-')[2]
    else:
        mm = date.split('-')[0]
        dd = date.split('-')[1]
    if dd[0] == '0':
        dd = dd[1]
    if mm[0] == '0':
        mm = mm[1]
    wd = dt.date(2017, int(mm), int(dd)).weekday() # return 0-6
    weekday = weekdayDict[int(wd)]    # monday-sunday
    return weekday


def customLowerMessageChecker(message):
	# Resposes for messages which u want to be be responsible 
    # phrases[0] - templates, phrases[1] - logs, phrases[2] - answers
    txt = message.text.lower()
    for phrases in customMessages:
        if len(phrases[0]) < 2:
            if phrases[0][0] in txt:
                logger(message, phrases[1])
                bot.send_message(message.chat.id, phrases[2], reply_markup=None)
                return 1
        else:
            for phrase in phrases[0]:
                if phrase in txt:
                    logger(message, phrases[1])
                    bot.send_message(message.chat.id, phrases[2], reply_markup=None)
                    return 1
    logger(message, 'send a "%s"' % txt)
    return 1


def customStickerMessageChecker(message):
	# If u have reactions message.text 
    for phrases in customStickerMessages:
        for msg in phrases[0]:
            if msg in message.text.lower():
                logger(message, phrases[1])
                try:
                    bot.send_message(message.chat.id, phrases[2], reply_markup=None)
                except:
                    pass
                # .webp - format for sticker pictures
                bot.send_sticker(message.chat.id, open('chozadano/stickers/'+phrases[3]+'.webp', 'rb'), reply_markup=None)
                return 1


def info_message(message):
	# Response for 'Info'
	# It can be maked by message_handlers, but no one wants 
	# to use this features throught commands ('/'). Buttons
	# are simpler than commands
    bot.send_message(message.chat.id, 'info message', reply_markup=None)
    logger(message, 'called info')
    return 1


def events_message(message):
	# Response for Events message
    @sqlAcces
    def getEvents(conn, cursor):
        cursor.execute('SELECT * FROM events')
        row = cursor.fetchone()
        response = ''
        while row is not None:
            date = [x for x in str(row[2]).split('-')]
            if date[2][0] == '0':    # If 0 before month
                date[2][0] == ''
            response += '%s %s - %sth (%s)\n' % (point, row[0], date[2], row[1])
            row = cursor.fetchone()
        bot.send_message(message.chat.id, response, reply_markup=None)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Hello, '+message.from_user.first_name+'!\U0001F604\n\nSome info\n\nU can learn feature events by press Events button\nMore about this bot by button Info',
                    reply_markup=markup)
    logger(message, 'start command')
    return 1


@bot.message_handler(commands=['noHW'])
# Admins function.
# If there is no homework for any of subjcts, u can
# erase homework for this subject. in otherwise case bot will send
# last week's homework for currentSubject() response.
def updateSubjToHZ(message):
    if message.from_user.id in admins_id_list:
        bot.send_message(message.chat.id, 'Enter name of subject, which HW will be erase',    reply_markup=None)
        def hz(message):
            @sqlAcces
            def putHZ(conn, cursor):
                subj = message.text
                if subj not in subjectsList:
                    bot.send_message(message.chat.id, 'No such subject', reply_markup=None)
                    return 1
                else:
                    cursor.execute('UPDATE subjects SET weekday=?,dateToExec=?,homework=? WHERE SubjName=?', ('nothing','nothing','no homework', subj))
                    conn.commit()
                    bot.send_message(message.chat.id, 'Succesfully erased HW for  '+subj, reply_markup=None)
                    return 1
                logger(message, 'erase HW for '+subj)
        bot.register_next_step_handler(message, hz)


@bot.message_handler(commands=['weather'])
# Admins function.
# Sended weather to all of users in rss_list table. Users appending to
# rss_list automaticly (see inBase())
def weathrResponse(message):
    if message.from_user.id in admins_id_list:
        @sqlAcces
        def getWthr(conn, cursor):
            cursor.execute('SELECT * FROM rss_list')
            row = cursor.fetchone()
            weatherMsg = weather.getWeather()
            while row is not None:
                bot.send_message(row[0], 'Good morning, ' + row[1] + '!' + weatherMsg, reply_markup=None)
                row = cursor.fetchone()
            logger(message, 'send weather')
            # 
            bot.send_message(message.chat.id, succes, reply_markup=None) 


@bot.message_handler(commands=['addevent'])
# Admins function.
def addevent(message):
    if message.from_user.id in admins_id_list:
    	# TODO: make remove by min date
        bot.send_message(message.chat.id, 'Remove last event/add new event? [1/2]', reply_markup=None)
        def defineAction(message):
            if message.text == '1':
                @sqlAcces
                def getSQL(conn, cursor):
                    cursor.execute('SELECT * FROM events')
                    row = cursor.fetchone()
                    lastdate = row[2]
                    cursor.execute('DELETE FROM events WHERE deadline=?', (lastdate, ))
                    bot.send_message(message.chat.id, 'Remove event '+row[0]+' with date '+lastdate, reply_markup=None)
                    logger(message, 'Remove event '+row[0]+' with date '+lastdate)
                    conn.commit()
                    return 1
            elif message.text == '2':
                bot.send_message(message.chat.id, 'Add event with format "Event - 02-06')
                def addEv(message):
                    @sqlAcces
                    def getSQL_(conn, cursor):
                        query = message.text.split(' - ')
                        cursor.execute('INSERT INTO events (eventName, weekDay, deadline) VALUES (?,?,?)', (query[0], defineWeekdayByDate(query[1]), '2017-'+query[1]))
                        bot.send_message(message.chat.id, 'Add event %s - %s - %s' % (query[0], defineWeekdayByDate(query[1]),'2017-'+query[1]))
                        conn.commit()
                        logger(message, 'Append event %s - %s - %s' % (query[0], defineWeekdayByDate(query[1]),'2017-'+query[1]))
                bot.register_next_step_handler(message, addEv)
            else:
                return 1
        bot.register_next_step_handler(message, defineAction)
    return 1


@bot.message_handler(commands=['addhomework'])
# Admins function.
# Bot will send instructions for input format to u, when u call this in chat
def addHomework(message):
    if message.from_user.id in admins_id_list:
        bot.send_message(message.chat.id, '\U0001F442', reply_markup=None)

        def validQuery(message):
            try:
                query = [x for x in str(message.text).split(' - ')]
                if (query[0] in subjectsList) and (len(query) == 3) and (len(query[1].split('-')) == 2) and (len(query[1]) in [4, 5]): # Date validation
                    weekday = defineWeekdayByDate(query[1])
                else:
                    logger(message, 'invalid query')
                    raise Exception
            except:
                bot.send_message(message.chat.id, 'Incorrect input', reply_markup=None)
                return 0
            @sqlAcces
            def add(conn, cursor):
                cursor.execute('''UPDATE subjects
                                    SET weekDay=?,dateToExec=?,homework=?
                                    WHERE SubjName=?''', (weekday, str('2017-' + query[1]), query[2], query[0]))
                conn.commit()
                bot.send_message(message.chat.id, succes+'success'+succes, reply_markup=None)
                logger(message, 'appended homework "%s"' % query[0])
                return 1

        bot.register_next_step_handler(message, validQuery)

    else:
        logger(message, 'tried to add homework without permission')
    return 1


@bot.message_handler(commands=['getlog'])
# Admins function.
# Sends log to u for data analysis
def getlog(message):
    if message.from_user.id in admins_id_list:
        LOG = open('chozadano/log.txt', 'rb')
        bot.send_document(224475156, LOG)
        LOG.close()
        # Clearing log. Information mustn't dulicates
        log_ = open('chozadano/log.txt', 'w')
        log_.close()
        logger(message, 'sended LOG')


@bot.message_handler(content_types=['text'])
def SubjectResponse(message):
    inBase(message)    # (for rss_list (weather))
    if message.text in subjectsList:
        logger(message, 'called homework for "%s"' % message.text)
        currentSubject(message)

    elif "what's tomorrow?" in message.text.lower() or 'hw' in message.text.lower():
        logger(message, '''called "what's tomorrow?"''')
        tomorrowHomework(message)

    elif "what's today?" in message.text.lower() or 'today' in message.text.lower():
        logger(message, 'called todayHW')
        todayHomework(message)

    elif 'events' in message.text.lower():
        logger(message, 'called events')
        events_message(message)

    elif 'info' in message.text.lower():
        logger(message, 'called info')
        info_message(message)

    else:
        customLowerMessageChecker(message)
        customStickerMessageChecker(message)

    return 1


@bot.message_handler(content_types=['audio'])
def audioResponse(message):
    logger(message, 'send an audio')
    bot.send_message(message.chat.id, 'Will listen it later)) (no)', reply_markup=None)


@bot.message_handler(content_types=['photo'])
def photoResponse(message):
    logger(message, 'send a photo')
    bot.send_message(message.chat.id, 'Lol', reply_markup=None)


@bot.message_handler(content_types=['sticker'])
def stickerResponse(message):
    logger(message, 'send a sticker')
    bot.send_message(message.chat.id, 'Wow, cute sticker, I will add this', reply_markup=None)


@bot.message_handler(content_types=['location'])
def locationResponse(message):
    logger(message, 'send a location')
    bot.send_message(message.chat.id, 'Here u are! We will find u.', reply_markup=None)


while True:
    try:
        # 100% none-stop service
        bot.polling(interval=1, none_stop=True)        
    except Exception as e:
        print(str(dt.datetime.now())[0:19]+' Exception:\n',e)
        with open(log_path + 'log.txt', 'a') as log:
            now = str(dt.datetime.now())[0:19]
            log.write(now + ' - server - Error!(%s)\n' % e)
        sleep(7)
        continue