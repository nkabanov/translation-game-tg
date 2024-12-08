import telebot
from telebot import types
bot = telebot.TeleBot('7513476604:AAFvXLsXpacPb9Rd9aZjvGXiEUhhvOFVE3w')
from regimes import Dictionary, spisok,Znachenie
import random
slovo = ''
answer = ''

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Словарь")
    btn2 = types.KeyboardButton("Легкая игра")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text="Привет, выберите интересующий вас режим.".format(message.from_user), reply_markup=markup)

@bot.message_handler(content_types=['text'])
def func(message):
    if (message.text == 'Словарь'):
        bot.send_message(message.chat.id, text="Введите интересующее вас слово.")
        bot.register_next_step_handler(message, slovar)

    elif (message.text == "Легкая игра"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать игру")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, back)
        bot.send_message(message.chat.id, text="Начните игру либо вернитесь в главное меню.".format(message.from_user), reply_markup=markup)

    elif (message.text == "Начать игру"):
        global answer
        answer = random.choice(spisok)
        global round
        round = 0
        bot.send_message(message.chat.id, f"{Znachenie(answer)}\n" 'Введите загаданое слово')

    elif ((message.text.upper() == answer) and round != 2):
        round = round+1
        answer = random.choice(spisok)
        bot.send_message(message.chat.id, 'Правильно!')
        bot.send_message(message.chat.id, f"{Znachenie(answer)}\n" 'Введите загаданое слово')

    elif (message.text == "Вернуться в главное меню"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Словарь")
        button2 = types.KeyboardButton("Легкая игра")
        markup.add(button1, button2)
        bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)

    elif (message.text.upper() != answer):
        round == 0
        bot.send_message(message.chat.id, 'Не правильно!\n' 'Загаданное слово:'+ str(answer))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать игру")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, back)
        bot.send_message(message.chat.id, text="Начните новую игру либо вернитесь в главное меню.".format(message.from_user), reply_markup=markup)

    elif (round==2):
        round == 0
        bot.send_message(message.chat.id, 'Поздравляем, вы прошли легкую игру!')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать игру")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, back)
        bot.send_message(message.chat.id, text="Начните новую игру либо вернитесь в главное меню.".format(message.from_user), reply_markup=markup)

def slovar(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back = types.KeyboardButton("Вернуться в главное меню")
    markup.add(back)
    global slovo
    slovo = message.text
    bot.send_message(message.chat.id, f"{Dictionary(slovo)}", reply_markup=markup)
    bot.register_next_step_handler(message, func)

bot.polling(none_stop=True)