import telebot
from pprint import pprint
import os
import database
import utils

bot = telebot.TeleBot(os.environ["TOKEN"])

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, '/help - сводка о командах\n' +
                          '/add - добавление разового напоминания напоминания\n'
                          # "Ваше сообщение" "дата в формате год.месяц.день часы.минуты.секунды" 
                          "/add_weekly - добавление повторяющегося напоминания в разные дни недели\n",
                          "/add_repeat - добавление повторяющегося напоминания с различным интервалом\n",
                          "/show_reminders - выводит информацию о всех имеющихся напоминаниях" 
                        ) 

@bot.message_handler(commands=['add'])
def save_note(message):
    raw_message = message.text.split()
    
    bad_text = "Неверно указанная команда. правильный формат: /add {message} {yyyy.mm.dd} {hh.mm.ss}"
    good_text = 'Напоминание "{}" успешно добавлено!'

    if (len(raw_message) < 4):
        bot.send_message(chat_id=message.chat.id, text=bad_text)
        return
    
    try:
        timestamp = utils.datetime_to_timestamp(raw_message[-2], raw_message[-1])
        message_to_save = ' '.join(raw_message[1:-2])
        chat_id=message.chat.id

        data = {"message" : message_to_save, "chat_id" : chat_id, "timestamp" : timestamp}
        database.insert_document(database.notes_collection, data)

        bot.send_message(chat_id=chat_id, text=good_text.format(message_to_save))
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text=bad_text)

@bot.message_handler(commands=['add_repeat'])
def save_repeat_note(message):
    raw_message = message.text.split()

    bad_text = "Неверно указанная команда. правильный формат: /add_repeat {message} {x}, где x время в секундах"
    good_text = 'Напоминание "{}" успешно добавлено!'

    if (len(raw_message) < 3):
        bot.send_message(chat_id=message.chat.id, text=bad_text)
    
    repeat_time = None
    if not raw_message[-1].isdigit():
        try:
            repeat_time = eval(raw_message[-1])
        except (SyntaxError, NameError):
            bot.send_message(chat_id=message.chat.id, text=bad_text)
            return
    else:
        repeat_time = int(raw_message[-1])
    
    message_to_save = ' '.join(raw_message[1:-1])
    chat_id=message.chat.id
    data = {"message" : message_to_save, 
            "chat_id" : chat_id, 
            "repeat_time" : repeat_time, 
            "current_timestamp" : utils.get_current_timestamp()}

    database.insert_document(database.repeat_notes_collection, data)

    bot.send_message(chat_id=chat_id, text=good_text.format(message_to_save))        

@bot.message_handler(commands=['show_reminders'])
def show_reminders(message):
    data = database.find_document(database.notes_collection, {"chat_id" : message.chat.id}, multiple=True)

    message_to_display = "Разовые напоминания:\n"

    for item in data:
        message_to_display += (item['message'] + " : " + utils.timestamp_to_date(item['timestamp']) + "\n")
    
    data = database.find_document(database.repeat_notes_collection, {"chat_id" : message.chat.id}, multiple=True)

    message_to_display += "Повторяющиеся напоминания:\n"

    for item in data:
        message_to_display += (item['message'] + " : Раз в " + str(item['repeat_time']) + " секунд\n")

    bot.send_message(chat_id=message.chat.id, text=message_to_display)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    pass

bot.polling(none_stop=True)