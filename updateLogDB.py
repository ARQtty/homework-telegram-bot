import sqlite3
import datetime as dt

conn = sqlite3.connect('./log_table.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE  log (year DATE, mounth DATE, day DATE, hours TIME, minuts TIME, seconds TIME, user VARCHAR, action VARCHAR)''')
now = str(dt.date.today())
subjectsList = ['Русский','Литература','Алгебра','Геометрия','История', 
				'Общага' ,'Физика'    ,'Химия'  ,'Биология' ,'География',
				'ИКТ'	 ,'Английский','ОБЖ'    ,'Экономика']

# Перенос из лога в базу
with open('./log.txt', 'r') as log:
	for line in log:
		line = line.replace('\n','')
		log_list = [str(x) for x in line.split(' - ')]
		date_and_time = [str(x) for x in log_list[0].split(' ')]
		date = [str(x) for x in date_and_time[0].split('-')]
		year = date[0]
		mounth = date[1]
		day = date[2]
		time = [str(x) for x in date_and_time[1].split(':')]
		hours = time[0]
		minuts = time[1]
		seconds = time[2]
		user = log_list[1]
		action = log_list[2]
		#print(year+'-'+mounth+'-'+day+'-'+hours+'-'+minuts+'-'+seconds+'-'+user+'-'+action)
		cursor.execute('''INSERT INTO log (year, mounth, day, hours, minuts, seconds, user, action)
							VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
							(year, mounth, day, hours, minuts, seconds, user, action))
conn.commit()
cursor.close()
conn.close()