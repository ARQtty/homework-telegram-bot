import sqlite3
import datetime as dt

conn = sqlite3.connect('homework-telegram-bot/subjects.sqlite')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS events (eventName VARCHAR, weekDay VARCHAR, deadline DATE)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (SubjName VARCHAR, weekDay VARCHAR, dateToExec VARCHAR, homework VARCHAR)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS rss_list (chat_id VARCHAR, Username VARCHAR)''')
conn.commit()
cursor.close()
conn.close()


conn = sqlite3.connect('homework-telegram-bot/log_table.sqlite')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS log (year DATE, mounth DATE, day DATE, hours TIME, minuts TIME, seconds TIME, user VARCHAR, action VARCHAR)''')
# Transfer log.txt data to DB
with open('homework-telegram-bot/log.txt', 'r') as log:
    for line in log:
        line = line.replace('\n','')
        log_info = [str(x) for x in line.split(' - ')]

        date_and_time = [str(x) for x in log_info[0].split(' ')]
        date = [str(x) for x in date_and_time[0].split('-')]
        year = date[0]
        mounth = date[1]
        day = date[2]
        
        time = [str(x) for x in date_and_time[1].split(':')]
        hours = time[0]
        minuts = time[1]
        seconds = time[2]
        
        user = log_info[1]
        action = log_info[2]
        #print(year+'-'+mounth+'-'+day+'-'+hours+'-'+minuts+'-'+seconds+'-'+user+'--'+action)
        cursor.execute('''INSERT INTO log (year, mounth, day, hours, minuts, seconds, user, action)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            (year, mounth, day, hours, minuts, seconds, user, action))
conn.commit()
cursor.close()
conn.close()