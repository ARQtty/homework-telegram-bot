from os import getcwd
import datetime as DT
from time import sleep
import urllib.request as req
import random
import sqlite3
import json

# Фреймворк PyTelegramBotAPI
import telebot


token = '362217833:AAHAd6fT3RnG34vtam0T4fDS3RQWgEjIhCw'
bot = telebot.TeleBot(token)
markup = telebot.types.ReplyKeyboardMarkup()

admins_id_list = [224475156]

# Путь ко всем файлам проекта
path = str(getcwd()) + '/'

subjectsList = ['Русский', 'Литература', 'Алгебра (1гр)', 'Алгебра (2гр)', 
				'Геометрия (1гр)', 'История','Обществознание', 'Физика', 'Химия', 
				'Биология', 'География', 'Геометрия (2гр)','ИКТ (1гр)', 
				'Английский (1гр)', 'ОБЖ', 'Английский (2гр)', 'Экономика', 'ИКТ (2гр)']

# Словарь кратких ответов
customMessages = [[['❤', '💙'],'send a ❤','И я тебя ❤'],
				  [['можешь'],'на слабо меня взял','Я всё могу!\U0001F64C'],
				  [['спасибо','спс','благодарю'],'поблагодарил', 'Пожалуйста)'] ]

# Пара смайлов
point = '\U000025AA'
succes = '\U00002705'

markup.row('Что на завтра?')
markup.row('События', 'Инфо')
markup.row('Погодку бы узнать')
markup.row('Русский', 'Литература')
markup.row('Алгебра (1гр)', 'Алгебра (2гр)')
markup.row('Геометрия (1гр)', 'Геометрия (2гр)')
markup.row('История', 'Общага')
markup.row('Физика', 'Химия')
markup.row('Биология', 'География')
markup.row('ИКТ (1гр)', 'ИКТ (2гр)')
markup.row('Английский (1гр)', 'Английский (2гр)')
markup.row('ОБЖ', 'Экономика')
markup.row('Что на сегодня?...')

polojenie = open(path + 'MTK2017.pdf', 'rb')


@bot.message_handler(commands=['addevent'])
def addevent(message):
	''' Добавление события '''
	# Разрешено только администратору
	if message.from_user.id in admins_id_list:
		bot.send_message(message.chat.id, 'Удалить последний event/добавить новый? [1/2]', reply_markup=None)
		def defineAction(message):
			if message.text == '1':
				@sqlAcces
				def getSQL(conn, cursor):
					# Удалим самое старое по дате событие
					cursor.execute('SELECT * FROM events')
					rows = sorted(cursor.fetchall(), key=lambda elem: elem[2])
					row = rows[0]
					lastdate = row[2]
					cursor.execute('DELETE FROM events WHERE deadline=?', (lastdate, ))
					bot.send_message(message.chat.id, 'Удалил событие '+row[0]+' с датой '+lastdate, reply_markup=None)
					logger(message, 'Удалил событие '+row[0]+' с датой '+lastdate)
					conn.commit()
					return
			# Добавим новое событие
			elif message.text == '2':
				bot.send_message(message.chat.id, 'Добавить event вида "Дежурство - 02-06')
				def addEv(message):
					@sqlAcces
					def getSQL_(conn, cursor):
						query = message.text.split(' - ')
						cursor.execute('INSERT INTO events (eventName, weekDay, deadline) VALUES (?,?,?)', (query[0], defineWeekdyByDate(query[1]), '2017-'+query[1]))
						bot.send_message(message.chat.id, 'Добавил событие %s - %s - %s' % (query[0], defineWeekdyByDate(query[1]),'2017-'+query[1]))
						conn.commit()
						logger(message, 'Добавил событие %s - %s - %s' % (query[0], defineWeekdyByDate(query[1]),'2017-'+query[1]))
				bot.register_next_step_handler(message, addEv)
			else:
				return
		bot.register_next_step_handler(message, defineAction)
	return


@bot.message_handler(commands=['addhomework'])
def addHomework(message):
	''' Добавление домашнего задания'''
	# Разрешено только администратору
	if message.from_user.id in admins_id_list:
		bot.send_message(message.chat.id, '\U0001F442', reply_markup=None)

		def validQuery(message):
			# Проверка валидности введённых данных о ДЗ
			try:
				query = [x for x in str(message.text).split(' - ')]
				if (query[0] in subjectsList):
					if (len(query) == 3):
						if (len(query[1].split('-')) == 2) or (len(query[1]) in [4, 5]): # Валидация даты
							weekday = defineWeekdyByDate(query[1])
						else:
							bot.send_message(message.chat.id, 'Неправильно указана дата. Она должна иметь вид "03-12" (12 марта)')
							logger(message, 'invalid query')
							raise Exception
					else:
						bot.send_message(message.chat.id, 'Нет пробелов между тире (или просто нет тире)')
						logger(message, 'invalid query')
						raise Exception
				else:
					bot.send_message(message.chat.id, 'Нет такого предмета')
					logger(message, 'invalid query')
					raise Exception
			except:
				bot.send_message(message.chat.id, 'Некорректный формат\nПравильный запрос:\nЛитература - 03-12 - ДЗ', reply_markup=None)
				return
			@sqlAcces
			def add(conn, cursor):
				# Если сообщение валидное, то запишем ДЗ в базу данных
				cursor.execute('''UPDATE subjects
									SET weekDay=?,dateToExec=?,homework=?
									WHERE SubjName=?''', (weekday, str('2017-' + query[1]), query[2], query[0]))
				conn.commit()
				bot.send_message(message.chat.id, succes+'Добавлено'+succes, reply_markup=None)
				logger(message, 'appended homework "%s"' % query[0])
				return

		bot.register_next_step_handler(message, validQuery)

	else:
		logger(message, 'tried to add homework without permission')
	return


def currentSubject(message):
	''' Отправка ДЗ по выбранному предмету '''
	@sqlAcces
	def getCrntSbj(conn, cursor):
		# Выборка по предмету
		cursor.execute('SELECT * FROM subjects WHERE SubjName=?', (message.text, ))
		homework = cursor.fetchone()
		if homework[3] in ['ничего не задано', 'Ничего не задано']:
			bot.send_message(message.chat.id, 'Ничего по этому предмету не задано')
		# Если что-то задано
		else:
			bot.send_message(message.chat.id, '%s - задано "%s" %s (%s)' % (message.text, homework[3], end(homework[2][6:]), homework[1]), reply_markup=None)
		return


def currentWeather_message(message):
	''' Ответ на запрос погоды '''
	weatherMsg = getWeather()
	bot.send_message(message.chat.id, weatherMsg, reply_markup=None)
	return


def customLowerMessageChecker(message):
	''' Проверка содержания текста присланного сообщения в словаре частых фраз
		phrases[0] - шаблоны, phrases[1] - логи, phrases[2] - ответы '''
	txt = message.text.lower()
	# Проверяем все фразы
	for phrases in customMessages:
		if len(phrases[0]) < 2:
			if phrases[0][0] in txt:
				logger(message, phrases[1])
				bot.send_message(message.chat.id, phrases[2], reply_markup=None)
				return
		else:
			for phrase in phrases[0]:
				if phrase in txt:
					logger(message, phrases[1])
					bot.send_message(message.chat.id, phrases[2], reply_markup=None)
					return
	logger(message, 'send a "%s"' % txt)
	return


def defineWeekdyByDate(date):
	''' По дате вида mm-dd или yyyy-mm-dd определяет день недели '''
	weekdayDict = {0: 'понедельник', 1: 'вторник', 2: 'среда', 3: 'четверг', 4: 'пятницо', 5: 'суббота', 6: 'воскресенье'}
	# Если формат yyyy-mm-dd
	if date[:4] == '2017':
		mm = date.split('-')[1]
		dd = date.split('-')[2]
	# Если формат mm-dd
	else:
		mm = date.split('-')[0]
		dd = date.split('-')[1]
	if dd[0] == '0':
		dd = dd[1]
	if mm[0] == '0':
		mm = mm[1]
	wd = DT.date(2017, int(mm), int(dd)).weekday() # вернёт число с 0 до 6
	weekday = weekdayDict[int(wd)]	# вернёт понедельник-воскресенье
	return weekday


def end(date):
	''' Упрощённая система определения падежа. Принимает mm-dd '''
	monthes = {1:'января', 2:'февраля',3:'марта',4:'апреля',5:'мая',6:'июня',7:'июля',8:'августа',9:'сентября',10:'октября',11:'ноября',12:'декабря'}
	date = date.split('-') # ['01', '07']
	# Чистим от лидирующих нулей
	if date[0][0] == '0':
		date[0] = date[0][1]
	if date[1][0] == '0':
		date[1] = date[1][1]
	month = monthes[int(date[0])]
	# Исключение: КО 2ому числу
	if date[1] == '2':
		date[1] = '2'
		pred = 'ко'
	else:
		pred = 'к'

	return pred + ' ' + date[1] + 'му ' + month


def events_message(message):
	''' Формирует ответ на запрос о ближайших событиях '''
	@sqlAcces
	def getEvents(conn, cursor):
		cursor.execute('SELECT * FROM events')
		rows = sorted(cursor.fetchall(), key=lambda elem: elem[2])
		response = ''
		for row in rows:
			date = [x for x in str(row[2]).split('-')]
			if date[2][0] == '0':	# Если 0 перед числом месяца
				date[2][0] == ''
			response += '%s %s - %se (%s)\n' % (point, row[0], date[2], row[1])
		bot.send_message(message.chat.id, response, reply_markup=None)


def getWeather():
    ''' Скрипт получения актуальной погоды в Санкт-Петербурге, перевода
		результата в иконочный, быстрочитаемый вид, русификация непереводимых
		сервисом параметров '''
    weatherEmojs  = {'Clouds':'\U00002601', 'Mist': '\U0001F301', 'Snow': '\U00002744', 'Clear': '\U0001F5FB', 'Rain': '\U00002614', 'Thunderstorm':'\U000026A1', 'Drizzle':'\U00002614'}
    statEms = {'tmp':'\U0001F4C8','prs':'\U0001F4AD','hyd':'\U0001F4A7','wnd':'\U0001F343','inf':'\U00002139'}
    url = "http://api.openweathermap.org/data/2.5/weather?q=Saint-Petersburg&mode=json&units=metric&appid=6151f42fb82c1ab87863da29465b594b&lang=ru"
    weatherMsg = '\n\nСейчас у нас:\n'
    # Обработка результата запроса
    with req.urlopen(url) as f:
        json_string = f.read().decode("utf-8")
        parsed_json = json.loads(json_string)
        sky = parsed_json["weather"][0]['main']
        sky_deskr = parsed_json["weather"][0]['description']
        temp = str(int(parsed_json['main']['temp']))
        vlajn = str(parsed_json['main']['humidity']) + '%'
        pressure = parsed_json['main']['pressure']
        windSpeed = str(parsed_json['wind']['speed']) + ' м/с'

    # Нормальное давление в Санкт-Петербурге: 102000-103500
    # Давление присылается в гектопаскалях
    if pressure in range(1020, 1035):
        pressure = 'нормальное'
    elif pressure in range(993, 1020):
        pressure = 'ниже нормы'
    elif pressure in range(0, 993):
    	pressure = 'низкое'
    elif pressure in range(1035, 1050):
        pressure = 'выше нормы'
    else:
    	pressure = 'высокое'
    # Если в словаре есть соответствующий погоде стикер - берём
    try:
        sk_em = weatherEmojs[sky]
    except:
        sk_em = weatherEmojs['Clouds']
    # Формирование сообщения о погоде
    weatherMsg += (statEms['tmp']+" Температура: "+temp+" C\n"
                           +sk_em+" На улице "+sky_deskr+"\n"
                  +statEms['prs']+" Давление "+pressure+"\n"
                  +statEms['hyd']+" Влажность воздуха: "+vlajn+"\n"
                  +statEms['wnd']+" Скорость ветра: "+windSpeed)
    return weatherMsg


def inBase(message):
	''' Проверка содержания chat_id пользователя в БД
		Вызывается при обработке каждого отправленного
		боту сообщения '''
	@sqlAcces
	def inbase(conn, cursor):
		# Выгружаем данные о уже зарегистрированных пользователях
		cursor.execute('SELECT * FROM rss_list')
		row = cursor.fetchone()
		users = []
		while row is not None:
				users.append(row[1])
				row = cursor.fetchone()

		# Если пользователь не найден - добавим		
		if message.from_user.first_name not in users:
			cursor.execute('INSERT INTO rss_list (chat_id, Username) VALUES (?, ?)', (message.chat.id, message.from_user.first_name))
			logger(message, 'Добавил пользователя %s в базу' % message.from_user.first_name)
		conn.commit()
		return


@bot.message_handler(commands=['help'])
def info_message(message):
	bot.send_message(message.chat.id, 'В жизни случается всякое. В том числе и простуда с температурой. Пусть ты и пропустил уроки, но домашнюю работу надо обязательно сделать! Этот бот скажет тебе, что задано, даже в 4 утра! Пользуйся наздоровье)', reply_markup=None)
	logger(message, 'called info')
	return


def logger(log_message, operation, err=False):
	''' Логгирование в файлы log.txt и errLog.txt '''

	# yyyy-mm-dd hh:mm:ss
	now = str(DT.datetime.now())[0:19]
	# Запись ошибок
	if err:
		with open(path + 'errLog.txt', 'a') as errLog:
			errLog.write(now + ' ' + log_message + '\n')
	# Запись логов
	else:
		with open(path + 'log.txt', 'a') as log:
			log.write(now + ' - ' + log_message.from_user.first_name + ' - ' + operation + '\n')


@bot.message_handler(commands=['polojenie'])
def polojenieResponse(message):
	''' Отправка любого документа. В данном случае - Положения о конференции '''
	logger(message, 'Скачал Положение')
	bot.send_document(message.chat.id, polojenie)


def sqlAcces(func):
	''' Декоратор для получения доступа к базе данных
		Помогает не забыть закрыть соединение с БД '''
	conn = sqlite3.connect(path + 'subjects.db')
	cursor = conn.cursor()
	
	# Даём conn для коммитов и cursor
	func(conn, cursor)
	
	cursor.close()
	conn.close()


@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id, 'Привет, '+message.from_user.first_name+'!\U0001F604\n\nКо мне можно обратиться за домашним заданием!\n\n\U00002B07Внизу\U00002B07 есть клавиатура выбора предмета, выбери нужный предмет и получишь последнее д/з по нему!\n\nУзнать предстоящие события можно с помощью кнопки События\nПоподробнее про бота - кнопка Инфо',
					reply_markup=markup)
	logger(message, 'start command')
	return


@bot.message_handler(content_types=['text'])
def SubjectResponse(message):
	''' Обработка всех пользовательских текстовых запросов '''

	# Есть ли пользователь в базе. Список пользователей используется
	# для массовой рассылки важной срочной информации
	inBase(message)

	# Если спросили дз по предмету
	if message.text in subjectsList:
		logger(message, 'called homework for "%s"' % message.text)
		currentSubject(message)
	
	# Если спросили ДЗ на завтра
	elif 'что на завтра' in message.text.lower():
		logger(message, 'called "Чо на завтра?"')
		tomorrowHomework(message)

	# Если спросили ДЗ на сегодня
	elif 'что на сегодня' in message.text.lower():
		logger(message, 'забывчивый человек, не помнит дз на сегодня')
		todayHomework(message)

	elif 'события' in message.text.lower():
		logger(message, 'посмотрел события')
		events_message(message)

	elif 'инфо' in message.text.lower():
		logger(message, 'посмотрел инфо')
		info_message(message)

	# Спросили погоду
	elif 'погодку бы узнать' in message.text.lower() or 'погода' in message.text.lower():
		logger(message, 'запросил погоду')
		currentWeather_message(message)

	# Попытаемся найти сообщение в базе кратких ответов
	else:
		customLowerMessageChecker(message)

	return


def todayHomework(message):
	''' Отправка сегодняшнего домашнего задания '''
	if defineWeekdyByDate(tomorrowDate()) == 'понедельник':
		bot.send_message(message.chat.id, 'Сегодня же воскресенье! Ни один садист не задаст дз на воскресенье!')
		return

	@sqlAcces
	def returnTomorrowHW(conn, cursor):
		# Извлекаем все ДЗ на завтра
		cursor.execute('SELECT * FROM subjects WHERE dateToExec=?', (DT.date.today(), ))
		row = cursor.fetchone()
		response = ''
		# Если извлечённое пусто
		if row is None:
			response = 'Ничего не задано'
		# Если что-то есть
		else:
			while row is not None:
				response += '%s %s - %s\n' % (point, row[0], row[3]) # КрасиваяТочка Предмет - дз
				row = cursor.fetchone()
		# Отправляем все ДЗ
		bot.send_message(message.chat.id, response, reply_markup=None)
		return


def tomorrowDate():
	''' Возвращает завтрашнюю дату в формате yyyy-mm-dd '''
	today = DT.date.today()
	tomorrow = str(today + DT.timedelta(days=1))
	return tomorrow


def tomorrowHomework(message):
	''' Отправка завтрашнего домашнего задания '''
	# Если завтра воскресенье
	if defineWeekdyByDate(tomorrowDate()) == 'воскресенье':
		bot.send_message(message.chat.id, 'Завтра воскресенье! Ты чего, кто делает дз в субботу?! Отличник что ли?!')
		return

	@sqlAcces
	def returnTwHW(conn, cursor):
		# Извлечь все ДЗ на завтра
		cursor.execute('SELECT * FROM subjects WHERE dateToExec=?', (tomorrowDate(), ))
		row = cursor.fetchone()
		response = ''
		# Если извлечённое пусто
		if row is None:
			response = 'Ничего не задано, можно катать в дотку весь день'
		# Если что-то есть
		else:
			while row is not None:
				response += '%s %s - %s\n' % (point, row[0], row[3]) # КрасиваяТочка Предмет - дз
				row = cursor.fetchone()

		# Если завтра есть какое-либо событие
		response += '\n'
		tomorrowDate_ = tomorrowDate()
		if tomorrowDate_[-2] == '0':
			tomorrowDate_ = tomorrowDate_[:-2] + tomorrowDate_[-1]
		cursor.execute('SELECT * FROM events WHERE deadline=?', (tomorrowDate_, ))
		row = cursor.fetchone()
		# Если событий нет
		if row is None:
			pass
		# Если есть
		else:
			while row is not None:
				response += point + row[0] + '\n'
				row = cursor.fetchone()

		# Отправляем ДЗ и события на завтра
		bot.send_message(message.chat.id, response, reply_markup=None)
		return


@bot.message_handler(commands=['hz'])
def updateSubjToHZ(message):
	''' Команда для удаления домашнего задания по выбранному предмету '''
	# Разрешено для администратору
	if message.from_user.id in admins_id_list:
		bot.send_message(message.chat.id, 'Имя предмета, по покоторому будет назначено "нет дз"?',	reply_markup=None)
		def hz(message):
			@sqlAcces
			def putHZ(conn, cursor):
				# Определили предмет, затираем ДЗ
				subj = message.text
				# Если ошиблись с названием
				if subj not in subjectsList:
					bot.send_message(message.chat.id, 'Нет такого предмета', reply_markup=None)
					return
				# Eсли такой предмет есть, затираем ДЗ по нему
				else:
					cursor.execute('UPDATE subjects SET weekday=?,dateToExec=?,homework=? WHERE SubjName=?', ('хз','хз','Ничего не задано', subj))
					conn.commit()
					bot.send_message(message.chat.id, 'Успешно затёр дз на '+subj, reply_markup=None)
					return
				logger(message, 'clear HW for '+subj)
		bot.register_next_step_handler(message, hz)



# Вечный цикл на обработку ошибок при работе
while True:
	try:
		# Поллинг
		bot.polling(interval=2.5, none_stop=True)
	except Exception as e:
		# Записать информацию об ошибке
		logger(str(e), 'null', err=True)
		# Подождать
		sleep(20)
		continue