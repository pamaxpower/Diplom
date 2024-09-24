
import re
import os
import telebot
from telebot import types
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

from processing import search_player, processing_players, check_date

from parser_tournaments import start_parser_tournament

from parser_games import my_func



pd.options.display.max_colwidth = 100

URL = 'https://www.sport-liga.pro/ru/table-tennis/tournaments'


# кнопки 1 этапа
def stage_1(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Турниры сегодня", "Турниры завтра")
    markup.row("Выбрать дату")
    bot.send_message(message.chat.id,
                     "Привет! 👋  Хотите посмотреть расписание турниров?",
                     reply_markup=markup)


# кнопки 2 этапа
def stage_2(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Поиск по игроку', 'Поиск по параметрам', 'Завершить работу')
    bot.send_message(message.chat.id, "Выберите дальнейшее действие:",
                     reply_markup=markup)



# функция получения датафрейма по дате
def get_df(message, dat):
    global data
    filename = f'./tours/tours_in_{dat}.csv'
    try:
        data = pd.read_csv(filename)

    except Exception as ex:
        bot.send_message(message.chat.id,
                         "Выполняется загрузка данных с сайта")
        start_parser_tournament(URL, dat)
        data = pd.read_csv(filename)
        bot.send_message(message.chat.id, "Турниры загружены")

    bot.send_message(message.chat.id, "Обрабатываю данные")
    data = processing_players(data)
    stage_2(message)


# функция обработки ввода даты
def check_date_input(message):
    dat = message.text
    global date
    try:
        dat = re.split(r'[,./]', message.text)
        if len(dat[2]) == 2:
            dat[2] = '20' + dat[2]
        if len(dat[1]) == 1:
            dat[1] = '0' + dat[1]
        if len(dat[0]) == 1:
            dat[0] = '0' + dat[0]
        selected_date = f'{dat[2]}-{dat[1]}-{dat[0]}'
        flag = check_date(selected_date)
        if flag:
            date = selected_date
        bot.send_message(message.chat.id, f"Дата '{date}' успешно  сохранена")
        get_df(message, selected_date)

    except Exception:
        bot.send_message(message.chat.id,
                         'Неверный формат даты. \
                            Пожалуйста, введите дату в формате ДД-ММ-ГГГГ:')
        bot.register_next_step_handler(message, check_date_input)


# загрузка токена для бота
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    TOKEN_BOT = os.getenv("TOKEN_BOT")

# Токен бота
bot = telebot.TeleBot(TOKEN_BOT)


# НАЧАЛО РАБОТЫ БОТА. Обработка /start
@bot.message_handler(commands=['start'])
def start(message):
    stage_1(message)


# Обработка ответов из 1 этапа
@bot.message_handler(
    func=lambda message: message.text in ["Турниры сегодня", "Турниры завтра",
                                          "Выбрать дату"])
def tournaments_today(message):
    global date

    if message.text == "Турниры сегодня":
        today = datetime.now().strftime('%Y-%m-%d')
        date = today
        bot.send_message(message.chat.id, f"Дата '{date}' успешно  сохранена",
                         get_df(message, date))


    elif message.text == "Турниры завтра":
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        date = tomorrow
        bot.send_message(message.chat.id,
                         f"Дата '{tomorrow}' успешно  сохранена", get_df(message, date))

    elif message.text == "Выбрать дату":
        bot.send_message(message.chat.id, "Введите дату в формате ДД-ММ-ГГГГ:")
        bot.register_next_step_handler(message, check_date_input)
    else:
        bot.send_message(message.chat.id, "Неверный выбор.")


# обработка кнопки "Поиск по игроку"
@bot.message_handler(func=lambda message: message.text == 'Поиск по игроку')
def search_by_player(message):
    # Получение имени игрока от пользователя
    bot.send_message(message.chat.id, "Введите фамилию игрока:")
    bot.register_next_step_handler(message, process_player_search)


# функция запуска поиска по фамилии
def process_player_search(message):
    global data
    # Получение имени игрока из сообщения
    player_name = message.text

    tours = search_player(player_name, data)
    if not tours.empty:
        for i, row in tours.iterrows():
            url_tours = row['url']
            keyboard = [[types.InlineKeyboardButton(
                "Перейти на страницу турнира", url=url_tours)]]
            reply_markup = types.InlineKeyboardMarkup(keyboard)

            row.drop('url', inplace=True)
            bot.send_message(message.chat.id, row.to_string(),
                             reply_markup=reply_markup)
    else:
        bot.send_message(message.chat.id, 'Такой игрок в эту дату не играет')

    stage_2(message)


# кнопки 3 этапа
def stage_3(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Выбрать стол')
    itembtn2 = types.KeyboardButton('Выбрать время')
    itembtn3 = types.KeyboardButton('Начать поиск')
    itembtn4 = types.KeyboardButton('Вернуться назад')
    markup.add(itembtn1, itembtn2, itembtn3)
    markup.add(itembtn4)

    bot.send_message(message.chat.id, "Что вы хотите сделать?",
                     reply_markup=markup)


# Данные для кнопок
tables = ['A3', 'A4', 'A5', 'A6', 'A9', 'A15']
times = ["07:30", "07:45", "08:00", "09:30", "11:30", "11:45", "12:00",
         "14:00",
         "15:30", "15:45", "16:00", "16:45", "18:30", "19:30", "19:45",
         "20:00",
         "20:30", "21:00", "23:30", "23:45"]

# Хранение выбранных опций
selected_tables = {}
selected_time = {}
value_tables = []
value_time = []


# обработка кнопки "Поиск по параметрам"
@bot.message_handler(
    func=lambda message: message.text == 'Поиск по параметрам')
def search_parameters(message):
    stage_3(message)


# обработка ответа "Выбрать стол"
@bot.message_handler(func=lambda message: message.text == 'Выбрать стол')
def select_table(message):
    markup = types.InlineKeyboardMarkup()
    buttons = []
    for table in tables:
        buttons.append(types.InlineKeyboardButton(table, callback_data=table))
    markup.add(*buttons[:3])
    markup.add(*buttons[3:])

    markup.add(types.InlineKeyboardButton("OK", callback_data="ok_tables"))
    bot.send_message(message.chat.id, "Выберите кнопки:", reply_markup=markup)


# обработка ответа "Выбрать время"
@bot.message_handler(func=lambda message: message.text == 'Выбрать время')
def select_time(message):
    markup = types.InlineKeyboardMarkup(row_width=3)

    for i in range(0, len(times), 3):
        row = []
        for j in range(i, min(i + 3, len(times))):
            row.append(
                types.InlineKeyboardButton(times[j], callback_data=times[j]))
        markup.row(*row)

    markup.add(types.InlineKeyboardButton("OK", callback_data="ok_times"))
    bot.send_message(message.chat.id, "Выберите кнопки:", reply_markup=markup)




# обработка нажатия на кнопки в выборе стола
@bot.callback_query_handler(func=lambda call: call.data in tables)
def table_callback(call):
    global selected_tables
    if call.data in selected_tables:
        selected_tables[call.data] = False
    else:
        selected_tables[call.data] = True

        # Обновляем текст кнопки
    button_text = call.data
    if selected_tables[call.data]:
        button_text += " ✅"
    else:
        button_text = call.data

        # Обновляем инлайн клавиатуру
    markup = types.InlineKeyboardMarkup()
    buttons = []
    for el in tables:
        button = types.InlineKeyboardButton(el, callback_data=el)
        if el in selected_tables:
            button.text += " ✅"
        buttons.append(button)

    markup.add(*buttons[:3])
    markup.add(*buttons[3:])

    markup.add(types.InlineKeyboardButton("OK", callback_data="ok_tables"))

    # Обновляем сообщение с инлайн клавиатурой
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите кнопки:",
        reply_markup=markup)


# обработка нажатия ОК в выборе стола
@bot.callback_query_handler(func=lambda call: call.data == "ok_tables")
def ok_table_callback(call):
    global selected_tables
    global value_tables

    selected_buttons = []
    for button, state in selected_tables.items():
        if state:
            selected_buttons.append(button)
    value_tables = list(selected_tables.keys())
    bot.send_message(call.message.chat.id,
                     f"Выбраны кнопки: {', '.join(selected_buttons)}")
    selected_tables = {}

    stage_3(call.message)


# обработка нажатия на кнопки в выборе времени
@bot.callback_query_handler(func=lambda call: call.data in times)
def time_callback(call):
    global selected_time

    if call.data in selected_time:
        selected_time[call.data] = not selected_time[call.data]
    else:
        selected_time[call.data] = True

    # Обновляем текст кнопки
    button_text = call.data
    if selected_time[call.data]:
        button_text += " ✅"
    else:
        button_text = call.data

    markup = types.InlineKeyboardMarkup()

    for i in range(0, len(times), 3):
        row = []
        for j in range(i, min(i + 3, len(times))):
            button = types.InlineKeyboardButton(times[j],
                                                callback_data=times[j])
            if times[j] in selected_time and selected_time[times[j]]:
                button.text += " ✅"
            row.append(button)
        markup.add(*row)

    markup.add(types.InlineKeyboardButton("OK", callback_data="ok_times"))

    # Обновляем сообщение с инлайн клавиатурой
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите кнопки:",
        reply_markup=markup
    )


# обработка нажатия ОК в выборе времени
@bot.callback_query_handler(func=lambda call: call.data == "ok_times")
def ok_time_callback(call):
    global selected_time
    global value_time

    selected_buttons = []
    for button, state in selected_time.items():
        if state:
            selected_buttons.append(button)
    value_time = list(selected_time.keys())
    bot.send_message(call.message.chat.id,
                     f"Выбраны кнопки: {', '.join(selected_buttons)}")
    selected_time = {}

    stage_3(call.message)



# обработка ответа "Начать поиск"
@bot.message_handler(func=lambda message: message.text == 'Начать поиск')
def search_by_parameters(message):
    """ """
    global value_tables
    global value_time
    global data
    global ut
    ut = []
    bot.send_message(
        message.chat.id,
        f"Вы выбрали параметры: {value_time} и {value_tables}"
    )

    filename = f'./tours/tours_in_{date}.csv'
    data = pd.read_csv(filename)
    processing_players(data)
    df = data.loc[
        data['tables'].isin(value_tables) & data['time'].isin(value_time)]
    if not df.empty:
        num = 1
        for i, row in df.iterrows():
            url_tours = row['url']
            ut.append(url_tours)

            keyboard = [[types.InlineKeyboardButton(
                "Перейти на страницу турнира", url=url_tours)],
                        [types.InlineKeyboardButton(
                            "Посмотреть статистику игроков",
                            callback_data=f"stats_players_{num}")]]

            reply_markup = types.InlineKeyboardMarkup(keyboard)

            row.drop('url', inplace=True)
            bot.send_message(message.chat.id, f'{row.to_string()}',
                             reply_markup=reply_markup)
            num += 1
    else:
        bot.send_message(message.chat.id,
                         'С такими параметрами турниры не найдены')
    stage_2(message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("stats_players_"))
def stat_players(call):
    global ut
    index = int(call.data.split('_')[2]) - 1
    bot.send_message(call.message.chat.id, 'Ожидайте загрузки')

    name = f'{ut[index].split("/")[-1]}'
    try:
        data1 = pd.read_csv(f'{name}.csv')

    except Exception:

        data1 = my_func(ut[index])
        print(ut, index)
        data1.to_csv(f'{name}.csv', index=False)

    bot.send_message(call.message.chat.id,
                     f'{data1.to_string(index=False, header=True, col_space=15)}')


# обработка кнопки "Вернуться назад"
@bot.message_handler(func=lambda message: message.text == 'Вернуться назад')
def go_back(message):
    stage_2(message)


# обработка кнопки "Завершить работу"
@bot.message_handler(func=lambda message: message.text == 'Завершить работу')
def end_session(message):
    bot.send_message(message.chat.id, "Работа завершена!")
    stage_1(message)


bot.polling(none_stop=True)



