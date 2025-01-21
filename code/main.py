import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove
import random
import logging
import unicodedata
import sqlite3
from regimes import Dictionary, spisok, Znachenie, Poisk_po_bukvam, Usage, Synonyms, sinonimi
from spisok_sokratscheniy import spisok_sokratschenij
from user_state import set_user_state, clear_user_state, get_user_state

bot = telebot.TeleBot('7513476604:AAFvXLsXpacPb9Rd9aZjvGXiEUhhvOFVE3w')
user_data = {}
logging.basicConfig(filename='feedback_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')



conn = sqlite3.connect("../data/feedback.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    feedback TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()
def remove_punctuation(text):
    text = unicodedata.normalize('NFKC', text)
    return text.strip().lower()

def send_main_menu(chat_id):
    user_data.pop(chat_id, None)
    clear_user_state(chat_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add("Легкая игра", "Сложная игра", "Словарь", "Оставить отзыв")
    bot.send_message(chat_id, "Выберите режим:", reply_markup=markup)

def ask_start_game(chat_id, game_mode):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Начать игру", "Вернуться в главное меню")
    bot.send_message(chat_id, f"Вы выбрали режим «{game_mode}». Начните игру или вернитесь в главное меню.", reply_markup=markup)
    set_user_state(chat_id, f'waiting_for_start_{game_mode}')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добро пожаловать в игру "Переводчик с русского на русский"!')
    bot.send_message(message.chat.id, 'Здесь вы можете узнать значение интересущего вас слова-англицизма, а также пройти несколько режимов игры для проверки своих знаний современного сленга.')
    send_main_menu(message.chat.id)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    user_text = remove_punctuation(message.text)
    if chat_id not in user_data:
        user_data[chat_id] = {'rounds': 1, 'tries': 3, 'words_list': [], 'current_answer': '', 'feedbacks': [], 'options': [], 'correct_answers': 0, 'used_words': []}

    if user_text == 'словарь':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Пользовательский ввод")
        markup.add("Поиск по буквам", "Список сокращений", "Главное меню")
        bot.send_message(chat_id, "Выберите способ поиска:", reply_markup=markup)

    elif user_text == 'главное меню' or user_text == 'вернуться в главное меню':
        send_main_menu(chat_id)

    elif user_text == 'пользовательский ввод':
        bot.send_message(chat_id, "Введите интересующее вас слово.")
        bot.register_next_step_handler(message, slovar)

    elif user_text == 'поиск по буквам':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for letter in "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦШЩЭЮЯ":
            markup.add(types.KeyboardButton(letter))
        bot.send_message(chat_id, "Выберите букву:", reply_markup=markup)
        bot.register_next_step_handler(message, Bukvennyi_poisk)

    elif user_text == 'список сокращений':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Пользовательский ввод")
        markup.add("Поиск по буквам", "Список сокращений", "Главное меню")
        bot.send_message(chat_id, spisok_sokratschenij, reply_markup=markup)

    elif user_text == 'оставить отзыв':
        bot.send_message(chat_id, "Пожалуйста, введите текст своего отзыва, указав имя, фамилию, возраст:", reply_markup=ReplyKeyboardRemove())
        set_user_state(chat_id, 'feedback')

    elif get_user_state(chat_id) == 'feedback':
        cursor.execute("INSERT INTO feedbacks (chat_id, feedback) VALUES (?, ?)", (chat_id, user_text))
        conn.commit()
        user_data[chat_id]['feedbacks'].append(user_text)
        logging.info(f"Feedback from {chat_id}: {user_text}")
        bot.send_message(chat_id, "Спасибо за ваш отзыв!")
        print(f'Feedback from {chat_id}: {user_text}')
        send_main_menu(chat_id)

    elif user_text == 'легкая игра':
        ask_start_game(chat_id, 'легкая игра')

    elif user_text == 'сложная игра':
        ask_start_game(chat_id, 'сложная игра')

    elif user_text == 'начать игру':
        user_state = get_user_state(chat_id) or ''
        if 'легкая игра' in user_state:
            start_easy_game(chat_id)
        elif 'сложная игра' in user_state:
            start_hard_game(chat_id)

    elif get_user_state(chat_id) == 'easy_game':
        check_easy_game_answer(chat_id, user_text)

    elif get_user_state(chat_id) == 'hard_game':
        check_hard_game_answer(chat_id, user_text)

def start_easy_game(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {'rounds': 1, 'tries': 3, 'words_list': [], 'current_answer': '', 'feedbacks': [], 'options': [], 'correct_answers': 0, 'used_words':[]}

    user_data[chat_id]['current_answer'] = random.choice(spisok)
    user_data[chat_id]['options'] = [Znachenie(user_data[chat_id]['current_answer'])] + random.sample(
        [Znachenie(w) for w in spisok if w != user_data[chat_id]['current_answer']], 2)
    random.shuffle(user_data[chat_id]['options'])

    user_data[chat_id]['rounds'] = 1
    user_data[chat_id]['tries'] = 3
    user_data[chat_id]['correct_answers'] = 0

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = [types.KeyboardButton(str(i + 1)) for i in range(3)]
    markup.add(*buttons, 'Главное меню')
    bot.send_message(chat_id,
                     f"Вопрос №{user_data[chat_id]['rounds']}\n\nНажмите на кнопку с номером, ответ под которым является определением слова: {user_data[chat_id]['current_answer']}\n\n" + "\n".join([f"{idx + 1}. {option}" for idx, option in enumerate(user_data[chat_id]['options'])]),
                     parse_mode="Markdown", reply_markup=markup)
    set_user_state(chat_id, 'easy_game')

def check_easy_game_answer(chat_id, user_text):
    if chat_id not in user_data or 'options' not in user_data[chat_id]:
        bot.send_message(chat_id, "Что-то пошло не так. Начните игру заново.")
        return
    available_words = [w for w in spisok if w not in user_data[chat_id]['used_words']]
    try:
        user_choice = int(user_text) - 1
        options = user_data[chat_id]['options']
        correct_option = Znachenie(user_data[chat_id]['current_answer'])
        if options[user_choice] == correct_option:
            user_data[chat_id]['used_words'].append(user_data[chat_id]['current_answer'])
            user_data[chat_id]['rounds'] += 1
            user_data[chat_id]['correct_answers'] += 1
            bot.send_message(chat_id, "Правильно!")
            if user_data[chat_id]['rounds'] >= 11:
                bot.send_message(chat_id,f"Игра завершена! Вы правильно ответили на {user_data[chat_id]['correct_answers']} вопросов из {user_data[chat_id]['rounds']-1}.")
                clear_user_state(chat_id)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add("Оставить отзыв", "Главное меню")
                bot.send_message(chat_id, "Пожалуйста, оставьте ваш отзыв об игре либо вернитесь в главное меню.", reply_markup=markup)
            else:
                user_data[chat_id]['current_answer'] = random.choice(available_words)
                user_data[chat_id]['options'] = [Znachenie(user_data[chat_id]['current_answer'])] + random.sample(
                    [Znachenie(w) for w in available_words if w != user_data[chat_id]['current_answer']], 2)
                random.shuffle(user_data[chat_id]['options'])
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                buttons = [types.KeyboardButton(str(i + 1)) for i in range(3)]
                markup.add(*buttons, 'Главное меню')
                bot.send_message(chat_id,
                                 f"Вопрос №{user_data[chat_id]['rounds']}\n\nНажмите на кнопку с номером, ответ под которым является определением слова: {user_data[chat_id]['current_answer']}\n\n" + "\n".join(
                                     [f"{idx + 1}. {option}" for idx, option in
                                      enumerate(user_data[chat_id]['options'])]),
                                 parse_mode="Markdown", reply_markup=markup)
        else:
            user_data[chat_id]['tries'] -= 1
            if user_data[chat_id]['tries'] != 0:
                user_data[chat_id]['used_words'].append(user_data[chat_id]['current_answer'])
                user_data[chat_id]['rounds'] += 1
                other_options = [option for option in options if option != correct_option]
                other_definitions = [
                    f"{word} - {Znachenie(word)}\n"
                    for word in spisok
                    if Znachenie(word) in other_options
                ]
                bot.send_message(chat_id,f"Неверно!\n\nПравильный ответ: {correct_option}\n")
                bot.send_message(chat_id, "Слова соответствующие другим вариантам ответов:\n\n\n" + "".join(other_definitions))
                bot.send_message(chat_id, f"Осталось жизней: {user_data[chat_id]['tries']}")
                user_data[chat_id]['current_answer'] = random.choice(available_words)
                user_data[chat_id]['options'] = [Znachenie(user_data[chat_id]['current_answer'])] + random.sample(
                    [Znachenie(w) for w in available_words if w != user_data[chat_id]['current_answer']], 2)
                random.shuffle(user_data[chat_id]['options'])
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                buttons = [types.KeyboardButton(str(i + 1)) for i in range(3)]
                markup.add(*buttons, 'Главное меню')
                bot.send_message(chat_id,
                                 f"Вопрос №{user_data[chat_id]['rounds']}\n\nНажмите на кнопку с номером, ответ под которым является определением слова: {user_data[chat_id]['current_answer']}\n\n" + "\n".join(
                                     [f"{idx + 1}. {option}" for idx, option in
                                      enumerate(user_data[chat_id]['options'])]),
                                 parse_mode="Markdown", reply_markup=markup)
            else:
                other_options = [option for option in options if option != correct_option]
                other_definitions = [
                    f"{word} - {Znachenie(word)}\n"
                    for word in spisok
                    if Znachenie(word) in other_options
                ]
                bot.send_message(chat_id, f"Неверно!\n\nПравильный ответ: {correct_option}\n")
                bot.send_message(chat_id,
                                 "Слова соответствующие другим вариантам ответов:\n\n\n" + "".join(other_definitions))
                bot.send_message(chat_id, f"Осталось жизней: {user_data[chat_id]['tries']}")
                bot.send_message(chat_id, f"Вы проиграли")
                clear_user_state(chat_id)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
                markup.add("Оставить отзыв", "Главное меню")
                bot.send_message(chat_id, "Пожалуйста, оставьте ваш отзыв об игре либо вернитесь в главное меню.",
                                 reply_markup=markup)

    except ValueError:
        bot.send_message(chat_id, "Введите число от 1 до 3.")

def start_hard_game(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {'rounds': 1, 'tries': 3, 'words_list': [], 'current_answer': '', 'feedbacks': [], 'options': [], 'correct_answers': 0, 'used_words':[]}
    bot.send_message(chat_id, 'Ответы на вопросы должны быть указаны в начальной форме:\n\nСуществительные в именительном падеже.\n\nПрилагательные в именительном падеже, единственном числе, мужском роде.\n\nГлаголы в инфинитиве.')
    available_words = [w for w in sinonimi if w not in user_data[chat_id]['used_words']]
    user_data[chat_id]['current_answer'] = random.choice(available_words)
    user_data[chat_id]['words_list'] = [remove_punctuation(w) for w in Synonyms(user_data[chat_id]['current_answer']).split(",") if w.strip()]
    user_data[chat_id]['rounds'] = 1
    user_data[chat_id]['tries'] = 3
    user_data[chat_id]['correct_answers'] = 0
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Главное меню")
    bot.send_message(chat_id, f"Вопрос №{user_data[chat_id]['rounds']}\n\nПо содержанию предложения определите значение слова {user_data[chat_id]['current_answer']} и укажите в строке сообщений русскоязычный синоним этого англицизма.\n\n{Usage(user_data[chat_id]['current_answer'])}", reply_markup=markup)
    set_user_state(chat_id, 'hard_game')

def check_hard_game_answer(chat_id, user_text):
    if chat_id not in user_data:
        bot.send_message(chat_id, "Что-то пошло не так. Начните игру заново.")
        return

    available_words = [w for w in sinonimi if w not in user_data[chat_id]['used_words']]
    if user_text in user_data[chat_id]['words_list']:
        user_data[chat_id]['used_words'].append(user_data[chat_id]['current_answer'])
        user_data[chat_id]['rounds'] += 1
        user_data[chat_id]['correct_answers'] += 1
        all_synonyms = user_data[chat_id]['words_list']
        bot.send_message(chat_id,f"Правильно!\n\nДопустимые варианты ответа: {', '.join(all_synonyms)}")
        if user_data[chat_id]['rounds']>=11:
            bot.send_message(chat_id,f"Игра завершена! Вы правильно ответили на {user_data[chat_id]['correct_answers']} вопросов из {user_data[chat_id]['rounds']-1}.")
            clear_user_state(chat_id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            markup.add("Оставить отзыв", "Главное меню")
            bot.send_message(chat_id, "Пожалуйста, оставьте ваш отзыв об игре либо вернитесь в главное меню.",
                             reply_markup=markup)
        else:
            user_data[chat_id]['current_answer'] = random.choice(available_words)
            user_data[chat_id]['words_list'] = [remove_punctuation(w) for w in
                                                Synonyms(user_data[chat_id]['current_answer']).split(",") if w.strip()]
            bot.send_message(chat_id, f"Вопрос №{user_data[chat_id]['rounds']}\n\nПо содержанию предложения определите значение слова {user_data[chat_id]['current_answer']} и укажите в строке сообщений русскоязычный синоним этого англицизма.\n\n{Usage(user_data[chat_id]['current_answer'])}")
    else:
        user_data[chat_id]['tries'] -= 1
        if user_data[chat_id]['tries'] != 0:
            bot.send_message(chat_id, f"Неверно!\n\nДопустимые варианты ответа: {', '.join(user_data[chat_id]['words_list'])}\n\nОсталось жизней: {user_data[chat_id]['tries']}")
            user_data[chat_id]['used_words'].append(user_data[chat_id]['current_answer'])
            user_data[chat_id]['rounds'] += 1
            user_data[chat_id]['current_answer'] = random.choice(available_words)
            user_data[chat_id]['words_list'] = [remove_punctuation(w) for w in
                                                Synonyms(user_data[chat_id]['current_answer']).split(",") if w.strip()]
            bot.send_message(chat_id,
                             f"Вопрос №{user_data[chat_id]['rounds']}\n\nПо содержанию предложения определите значение слова {user_data[chat_id]['current_answer']} и укажите в строке сообщений русскоязычный синоним этого англицизма.\n\n{Usage(user_data[chat_id]['current_answer'])}")
        else:
            bot.send_message(chat_id, f"Неверно!\n\nДопустимые варианты ответа: {', '.join(user_data[chat_id]['words_list'])}")
            bot.send_message(chat_id, f"Осталось жизней: {user_data[chat_id]['tries']}")
            bot.send_message(chat_id, f"Вы проиграли")
            clear_user_state(chat_id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            markup.add("Оставить отзыв", "Главное меню")
            bot.send_message(chat_id, "Пожалуйста, оставьте ваш отзыв об игре либо вернитесь в главное меню.",
                             reply_markup=markup)
def slovar(message):
    chat_id = message.chat.id
    slovo = remove_punctuation(message.text)
    result = Dictionary(slovo)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Пользовательский ввод")
    markup.add("Поиск по буквам", "Список сокращений", "Главное меню")
    bot.send_message(chat_id, result if result else "Слово не найдено.", reply_markup=markup)


def Bukvennyi_poisk(message):
    chat_id = message.chat.id
    letter = message.text.upper()
    words = Poisk_po_bukvam(letter)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for word in words:
        markup.add(types.KeyboardButton(word))
    bot.send_message(chat_id, f"Выберите слово на букву {letter}:", reply_markup=markup)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Пользовательский ввод")
    markup.add("Поиск по буквам", "Список сокращений", "Главное меню")
    bot.register_next_step_handler(message, slovar)


bot.polling(none_stop=True)
