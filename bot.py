import telebot
import os

bot = telebot.TeleBot(os.environ["TOKEN"])

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, '/help - сводка о командах\n' +
                          '/add - добавление разового напоминания напоминания\n'
                          # "Ваше сообщение" "дата в формате часы.минуты/день.месяц.год" 
                          "/add_repeat - добавление повторяющегося напоминания"
                        ) 

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    pass
        
print("It is works!")
bot.polling(none_stop=True)