import telebot
#from pprint import pprint
import os
import database
import utils

bot = telebot.TeleBot(os.environ["TOKEN"])

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, '/help - сводка о командах\n' +
                          '/add - добавление разового напоминания напоминания\n'
                          # "Ваше сообщение" "дата в формате год.месяц.день часы.минуты.секунды" 
                          "/add_repeat - добавление повторяющегося напоминания",
                          "/show_reminders - выводит информацию о всех имеющихся напоминаниях" 
                        ) 

@bot.message_handler(commands=['add'])
def save_note(message):
    raw_message = message.text.split()
    
    bad_text = "Неверно указанная команда. правильный формат: /add {message} {yyyy.mm.dd} {hh.mm.ss}"
    good_text = 'Напоминание "{}" успешно добавлено!'

    if (len(raw_message) < 4):
        bot.send_message(chat_id=message.chat.id, text=bad_text)
    
    try:
        timestamp = utils.datetime_to_timestamp(raw_message[-2], raw_message[-1])
        message_to_save = ' '.join(raw_message[1:-2])
        chat_id=message.chat.id

        data = {"message" : message_to_save, "chat_id" : chat_id, "timestamp" : timestamp}
        database.insert_document(database.notes_collection, data)

        bot.send_message(chat_id=chat_id, text=good_text.format(message_to_save))
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text=bad_text)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    pass

bot.polling(none_stop=True)