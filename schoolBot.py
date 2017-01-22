import sqlite3
import datetime as DT

import telebot

token = 'your token'
admins_id_list = ['admin id']
log_path = './'
bot = telebot.TeleBot(token)
markup = telebot.types.ReplyKeyboardMarkup()
subjectsList = ['Русский', 'Литература', 'Алгебра', 'Геометрия', 'История',
				'Общага', 'Физика', 'Химия', 'Биология', 'География',
				'ИКТ', 'Английский', 'ОБЖ', 'Экономика']
weekdayDict = {0: 'понедельник', 1: 'вторник', 2: 'среда', 3: 'четверг', 4: 'пятницо', 5: 'суббота', 6: 'воскресенье'}

customMessages = [[['❤', '💙'],'send a ❤','И я тебя ❤'],
				  [['))'],'улыбнулся мне','))0)'],
				  [['предмет'],'send a "Предмет" message','Предмет - не предмет'],
				  [['можешь'],'на слабо меня взял','Я всё могу!\U0001F64C'],
				  [['ларин'],'Ларина вспомнил','\U0001F414 это он?'],
				  [['илья'],'с маленькой буквы имя господина написали','С БОЛЬШОЙ БУКВЫ ИМЯ ГОСПОДИНА'],
				  [['дмитрий', 'павлович', 'дп'],'вспомнил ДП','Я просто оставлю это здесь\nrussianfood.com/recipes/bytype/?fid=963'],
				  [['марат'],'вспомнил Маратика','Я помню Марата. Знаком с ним, можно сказать. Каждый раз, когда он отправляет мне сообщение, у меня в транзисторах возникают эти строки:\n\n  Я помню чудное мгновенье:\nПередо мной явился ты,\nКак мимолетное виденье,\nКак гений чистой красоты.\n\n  В томленьях грусти безнадежной\nВ тревогах шумной суеты,\nЗвучал мне долго голос нежный\nИ снились милые черты.\n\nЕго черты...\U0001F60D'],
				  [['лапочка'],'форевер элон','Люблю тебя,зайка'] ]

customStickerMessages = [['хова','хованского вспомнил','','greben'],
						 ['прив','поприветствовал меня','приветик!\U0001F44B','oHello'],
						 ['окс','Ксюху вспомнил','','oO'],
						 ['как дела','спросил меня "как дела". Рукалицо','Ты серьёзно?! Ты спрашиваешь у бота, как у него дела?!','oShock'],
						 [' дела?','спросил меня "как дела". Рукалицо','Ты серьёзно?! Ты спрашиваешь у бота, как у него дела?!','oShock'],
						 ['что делаеш','спросил меня "как дела". Рукалицо','Ты серьёзно?! Ты спрашиваешь у бота, как у него дела?!','oShock']]

one = '\U00000031\U000020E3'
two = '\U00000032\U000020E3'
three = '\U00000033\U000020E3'
four = '\U00000034\U000020E3'
five = '\U00000035\U000020E3'
six = '\U00000036\U000020E3'
seven = '\U00000037\U000020E3'
eight = '\U00000038\U000020E3'
point = '\U000025AA'
# События
# Дежурства
# Конспекты
# Сделать авторемув

markup.row('Чо на завтра?')
markup.row('Русский', 'Литература')
markup.row('Алгебра', 'Геометрия')
markup.row('История', 'Общага')
markup.row('Физика', 'Химия')
markup.row('Биология', 'География')
markup.row('ОБЖ', 'Экономика')


def logger(log_message, operation):
	with open(log_path + 'log.txt', 'a') as log:
		now = str(DT.datetime.now())[0:19]
		log.write(now + ' - ' + log_message.from_user.first_name + ' - ' + operation + '\n')


def tomorrowDate():
	# Возвращает yyyy-mm-dd
	today = DT.date.today()
	tomorrow = str(today + DT.timedelta(days=1))
	return tomorrow


def end(date):
	# Упрощённая система определения падежа
	# Принимает мм-дд (01-15, 02-01, 02-4)
	date = date.split('-')
	if date[1][0] == '0':	# Если 0 перед числом месяца
		date[1][0] == ''
	if date[0] in ['1', '01']:
		mounth = 'января'
	elif date[0] in ['2', '02']:
		mounth = 'февраля'
	if date[1] in ['2', '02']:	# КО 2ому числу. Исключение
		date[1] = '2'
		pred = 'ко'
	elif date[1][0] == '0':
		date[1] = date[1][1]
		pred = 'к'
	else:
		pred = 'к'
	return pred + ' ' + date[1] + 'му ' + mounth


def tomorrowHomework(message):
	if defineWeekdyByDate(tomorrowDate()) == 'воскресенье':	# Если завтра воскресенье
		bot.send_message(message.chat.id, 'Завтра воскресенье! Ты чего, кто делает дз в субботу?! Отличник что ли?!')
		return 1

	conn = sqlite3.connect('./subjects.db')
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM subjects WHERE dateToExec=?', (tomorrowDate(), ))	# Извлечь все ДЗ на завтра
	row = cursor.fetchone()
	response = ''
	if row is None:	# Если извлечённое пусто
		response = 'Ничего не задано, можно катать в дотку весь день'
	else:
		while row is not None:
			response += '%s %s - %s\n' % (point, row[0], row[3]) # Предмет - дз
			row = cursor.fetchone()
	bot.send_message(message.chat.id, response, reply_markup=None) # Отправляем все ДЗ на завтра
	cursor.close()
	conn.close()
	return 1


def currentSubject(message):
	conn = sqlite3.connect('./subjects.db')
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM subjects WHERE SubjName=?', (message.text, )) # Выборка по предмету
	homework = cursor.fetchone()
	if homework[3] in ['ничего не задано', 'Ничего не задано']:
		bot.send_message(message.chat.id, 'Ничего по этому предмету не задано')
	else:
		bot.send_message(message.chat.id, '%s - задано "%s" %s (%s)' % (message.text, homework[3], end(homework[2][6:]), homework[1]), reply_markup=None)
	cursor.close()
	conn.close()
	return 1


def defineWeekdyByDate(date):
	# Должна получать mm-dd или yyyy-mm-dd
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
	wd = DT.date(2017, int(mm), int(dd)).weekday() # вернёт 0-6
	weekday = weekdayDict[int(wd)]	# понедельник-воскресенье
	return weekday


def customLowerMessageChecker(message):
	# phrases[0] - шаблоны, phrases[1] - логи, phrases[2] - ответы
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
	for phrases in customStickerMessages:
		if phrases[0] in message.text.lower():
			logger(message, phrases[1])
			try:
				bot.send_message(message.chat.id, phrases[2], reply_markup=None)
			except:
				pass
			bot.send_sticker(message.chat.id, open('./stickers/'+phrases[3]+'.webp', 'rb'), reply_markup=None)
			return 1

@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id, 'Привет, '+message.from_user.first_name+'!\U0001F604\n\nКо мне можно обратиться за домашним заданием!\n\n\U00002B07Внизу\U00002B07 есть клавиатура выбора предмета, выбери нужный предмет и получишь последнее д/з по нему!\n\nУзнать предстоящие события можно с помощью команды /events\nПоподробнее про бота можно узнать с помощью /info',
					reply_markup=markup)
	logger(message, 'start command')
	return 1


@bot.message_handler(commands=['info'])
def info_message(message):
	bot.send_message(message.chat.id, 'Мы часто слышим\n"ВЫ МЕНЯ ВСЕ ЗАЕ\U0001F4A5\U0001F4A5ЛИ\СКАЖИ ДЗ\nСКИНЬ КОНСПЕКТЫ\nА КАК ЭТО ДЕЛАТЬ\nДАЙ СПИСАТЬ\nПОМОГИ\nУ МЕНЯ ВЫХОДНОЙ",\nЭтот бот - замечательное решение проблемы! Он отвечат в течение секунд\U000023F0, почти в любое время и никогда вас не пошлёт.\n\nКонкретно по боту:\n '+one+'фраза1\n '+two+'фраза2\n '+three+'фраза3\n '+four+'фраза 4\n '+five+'фраза5', reply_markup=None)
	logger(message, 'called info')
	return 1


@bot.message_handler(commands=['events'])
def events_message(message):
	conn = sqlite3.connect('./subjects.db')
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM events')
	row = cursor.fetchone()
	response = ''
	while row is not None:
		date = [x for x in str(row[2]).split('-')]
		if date[2][0] == '0':	# Если 0 перед числом месяца
			date[2][0] == ''
		response += '%s %s - %se (%s)\n' % (point, row[0], date[2], row[1])
		row = cursor.fetchone()
	cursor.close()
	conn.close()
	bot.send_message(message.chat.id, response, reply_markup=None)


@bot.message_handler(commands=['addhomework'])
def addHomework(message):
	if message.from_user.id in admins_id_list:
		logger(message, 'succes logged as admin')
		# Добавить сообщение для Оксаны
		bot.send_message(message.chat.id, 'Предмет - на какой день (например 16 янв: 01-16) - дз', reply_markup=None)

		def validQuery(message):
			try:
				query = [x for x in str(message.text).split(' - ')]
				if (query[0] in subjectsList) and (len(query) == 3) and (len(query[1].split('-')) == 2) and (len(query[1]) in [4, 5]): # Валидация даты
					weekday = defineWeekdyByDate(query[1])
					logger(message, 'succes query append - %s' % query)
				else:
					logger(message, 'unvalid query')
					raise Exception
			except:
				bot.send_message(message.chat.id, 'Некорректный формат ввода', reply_markup=None)
				return 0

			conn = sqlite3.connect('./subjects.db')
			cursor = conn.cursor()
			cursor.execute('''UPDATE subjects
								SET weekDay=?,dateToExec=?,homework=?
								WHERE SubjName=?''', (weekday, str('2017-' + query[1]), query[2], query[0]))
			conn.commit()
			cursor.close()
			conn.close()
			bot.send_message(message.chat.id, '\U00002705Добавлено\U00002705', reply_markup=None)
			logger(message, 'appended homework "%s"' % query[0])
			return 1

		bot.register_next_step_handler(message, validQuery)

	else:
		bot.send_message(message.chat.id, 'Ты не админ, твои руки могут оказаться кривыми и убить бота', reply_markup=None)
		logger(message, 'tried to add homework without permission')
	return 1


@bot.message_handler(content_types=['text'])
def SubjectResponse(message):
	if message.text in subjectsList:
		logger(message, 'called homework for "%s"' % message.text)
		currentSubject(message)

	elif message.text == 'чо на завтра?' or 'чо на завтра' in message.text.lower() or 'дз' in message.text.lower():
		logger(message, 'called "Чо на завтра?"')
		tomorrowHomework(message)

	elif message.text.lower() in 'я':
		logger(message, 'нарицсс чёртов')
		bot.send_message(message.chat.id, 'Последняя буква алфавита.', reply_markup=None)

	elif 'Илья' in message.text:
		logger(message, 'упоминули имя моё')
		bot.send_message(message.chat.id, 'Имя господина нашего звучит подобно музыке', reply_markup=None)

	else:
		customLowerMessageChecker(message)
		customStickerMessageChecker(message)

	return 1


@bot.message_handler(content_types=['audio'])
def audioResponse(message):
	logger(message, 'send an audio')
	bot.send_message(message.chat.id, 'Потом как-нибудь послушаю)) (нет)', reply_markup=None)


@bot.message_handler(content_types=['document'])
def documentResponse(message):
	logger(message, 'send a documet')
	bot.send_message(message.chat.id, 'Чёт не открывается', reply_markup=None)


@bot.message_handler(content_types=['photo'])
def photoResponse(message):
	logger(message, 'send a photo')
	bot.send_message(message.chat.id, 'Лол', reply_markup=None)


@bot.message_handler(content_types=['sticker'])
def stickerResponse(message):
	logger(message, 'send a sticker')
	bot.send_message(message.chat.id, 'Клёвый стикер, надо будет добавить себе', reply_markup=None)


@bot.message_handler(content_types=['location'])
def locationResponse(message):
	logger(message, 'send a location')
	bot.send_message(message.chat.id, 'Вот ты где! Ну всё, за тобой выехали.', reply_markup=None)


@bot.message_handler(content_types=['voice'])
def voiceResponse(message):
	logger(message, 'send a voice')
	bot.send_message(message.chat.id, 'У тебя голос, как у маленькой девочки.', reply_markup=None)

bot.polling(interval=3)
