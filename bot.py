import os

from threading import Thread
from time import sleep

import telebot
import schedule

import database
import utils


bot = telebot.TeleBot(os.environ["TOKEN"])


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 
                '/help - сводка о командах\n' +
                '/add - добавление разового напоминания напоминания\n'
                # "/add_weekly - добавление повторяющегося напоминания в разные дни недели\n",
                "/add_repeat - добавление повторяющегося напоминания с различным интервалом\n",
                "/show - выводит информацию о всех имеющихся напоминаниях" 
                ) 


@bot.message_handler(commands=['add'])
def read_message(message):
    msg = bot.reply_to(message, 'Введите название напоминания')
    bot.register_next_step_handler(msg, read_date)

def read_date(message):
    data = [message.text]
    msg = bot.reply_to(message, 'Введите дату напоминания в формате {yyyy.mm.dd}')
    bot.register_next_step_handler(msg, read_time, data)

def read_time(message, data):
    data.append(message.text)
    msg = bot.reply_to(message, 'Введите время напоминания в формате {hh:mm:ss}')
    bot.register_next_step_handler(msg, compute_note, data)

def compute_note(message, data):
    data.append(message.text)

    bad_text = "Введены некорректные данные, напоминание {} не было добавлено".format(data[0])
    good_text = 'Напоминание "{}" успешно добавлено!'

    try:
        timestamp = utils.datetime_to_timestamp(data[-2], data[-1])
        message_to_save = data[0]
        chat_id=message.chat.id

        data = {"message" : message_to_save, "chat_id" : chat_id, "timestamp" : timestamp}
        database.insert_document(database.notes_collection, data)

        bot.send_message(chat_id=chat_id, text=good_text.format(message_to_save))
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text=bad_text)

@bot.message_handler(commands=['add_repeat'])
def read_message_repeat(message):
    msg = bot.reply_to(message, 'Введите название напоминания')
    bot.register_next_step_handler(msg, read_time_repeat)

def read_time_repeat(message):
    data = [message.text]
    msg = bot.reply_to(message, 
                    'Введите интервал повторения напоминания в секундах в формате числа или выражения')

    bot.register_next_step_handler(msg, compute_note_repeat, data)

def compute_note_repeat(message, data):
    data.append(message.text)

    bad_text = "Введены некорректные данные, напоминание {} не было добавлено".format(data[0])
    good_text = 'Напоминание "{}" успешно добавлено!'
    
    repeat_time = None
    if not data[-1].isdigit():
        try:
            repeat_time = eval(data[-1])
        except (SyntaxError, NameError):
            bot.send_message(chat_id=message.chat.id, text=bad_text)
            return
    else:
        repeat_time = int(data[-1])
    
    message_to_save = data[0]
    chat_id=message.chat.id
    data = {"message" : message_to_save, 
            "chat_id" : chat_id, 
            "repeat_time" : repeat_time, 
            "current_timestamp" : utils.get_current_timestamp()}

    database.insert_document(database.repeat_notes_collection, data)

    bot.send_message(chat_id=chat_id, text=good_text.format(message_to_save)) 


@bot.message_handler(commands=['show', "dismiss"])
def show_reminders(message):
    data_once = database.find_document(database.notes_collection, {"chat_id" : message.chat.id}, multiple=True)

    count = 1

    message_to_display = "Разовые напоминания:\n"

    for item in data_once:
        message_to_display += (str(count) + ") " + item['message'] + " : " + utils.timestamp_to_date(item['timestamp']) + "\n")
        item["id"] = count
        count += 1
    
    data_repeat = database.find_document(database.repeat_notes_collection, {"chat_id" : message.chat.id}, multiple=True)

    message_to_display += "Повторяющиеся напоминания:\n"

    for item in data_repeat:
        message_to_display += (str(count) + ") " + item['message'] + " : Раз в " + str(item['repeat_time']) + " секунд\n")
        item["id"] = count
        count += 1
    bot.send_message(chat_id=message.chat.id, text=message_to_display)

    if message.text.split()[0] == "/dismiss":
        data = data_once + data_repeat
        msg = bot.reply_to(message, 'Введите номер удаляемого элемента. 0 для отмены, -1 для удаления всего')
        bot.register_next_step_handler(msg, dismiss_reminders, data)

def dismiss_reminders(message, data):
    try:
        id_to_delete = int(message.text)

        for item in data:
            if id_to_delete == -1:
                database.delete_document(database.notes_collection, {"_id" : item["_id"]})
                database.delete_document(database.repeat_notes_collection, {"_id" : item["_id"]})
            elif item["id"] == id_to_delete:
                database.delete_document(database.notes_collection, {"_id" : item["_id"]})
                database.delete_document(database.repeat_notes_collection, {"_id" : item["_id"]})
                bot.reply_to(message, "Удалено")
                return
    except ValueError:
        bot.reply_to(message, "Некоректные данные")
        return
    
    if (int(message.text) == 0):
        bot.reply_to(message, "Отменено")
    elif(int(message.text) == -1):
        bot.reply_to(message, "Все напоминания удалены")
    else:
        bot.reply_to(message, "Номер найти не удалось")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    pass


def remind():
    data = database.find_document(database.notes_collection, {}, multiple=True)

    for item in data:
        if utils.get_current_timestamp() >= item["timestamp"]:
            chat_id = item["chat_id"]
            message = item["message"]

            database.delete_document(database.notes_collection, {"_id" : item["_id"]})

            bot.send_message(chat_id=chat_id, text=message)
    
    data = database.find_document(database.repeat_notes_collection, {}, multiple=True)

    for item in data:
        if (utils.get_current_timestamp() - item["current_timestamp"]) % item["repeat_time"] == 0:
            chat_id = item["chat_id"]
            message = item["message"]

            bot.send_message(chat_id=chat_id, text=message)



def schedule_check():
    while True:
        schedule.run_pending()
        sleep(1)

if __name__ == "__main__":
    schedule.every(1).second.do(remind)
    Thread(target=schedule_check).start() 

    bot.enable_save_next_step_handlers(delay=2)
    bot.polling(none_stop=True)