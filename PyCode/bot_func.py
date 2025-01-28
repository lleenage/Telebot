import telebot
import random
from dotenv import load_dotenv
import os
from telebot import types, custom_filters
from telebot.handler_backends import StatesGroup, State
from sqlalchemy.orm import sessionmaker
from telebot.storage import StateMemoryStorage

from main import engine
from sql_func import User, Personal_words, Basic_words

dotenv_path = "../private/confirm.env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

telebot_token = os.getenv('TOKEN_TELEBOT')

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(telebot_token)


known_users = []
userStep = {}
buttons = []

russian_words = [i.russian_word for i in (sessionmaker(bind=engine))().query(Basic_words).all()]
english_words = [i.english_word for i in (sessionmaker(bind=engine))().query(Basic_words).all()]
target_w = (sessionmaker(bind=engine))().query(Basic_words.english_word)
(sessionmaker(bind=engine))().close()

def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"

def show_hint(*lines):
    return '\n'.join(lines)

def get_user_step(user_name, user_id):
    if user_id in userStep:
        return userStep[user_id]
    else:
        known_users.append(user_id, user_name)
        userStep[user_id] = 0
        print("Новый пользователь, который eще не использовал '/start'")
        return 0

class Commands:
    add = 'Добавить слово ➕'
    delete = 'Удалить слово 🔙'
    next = 'Следующее слово ⏭'

class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    other_words = State()




def add_users(engine, user_id, user_name):   #функция добавляющая пользователя в бд с параметрами user_id, user_name
    session = (sessionmaker(bind=engine))()
    session.add(User(cid=user_id, name=user_name))
    for i in session.query(User).all():
        print(f'Пользовтель: {i}')
        print(known_users)
    session.commit()
    session.close()

def add_personal_word(engine, russian_word: str, english_word: str): #функция для добавления слов в бд
    session = (sessionmaker(bind=engine))()
    session.add(Personal_words(russian_word=russian_word, english_word=english_word, user_id=User.id))
    session.commit()
    session.close()

def delete_word(del_word):
    import re

    session = (sessionmaker(bind=engine))()
    if re.search(r'[^а-яА-Я]', del_word):
        session.query(Personal_words).filter(Personal_words.russian_word == del_word).delete() # удаляем объект
    elif re.search(r'[^a-zA-Z]', del_word):
        session.query(Personal_words).filter(Personal_words.english_word == del_word).delete() # удаляем объект
    session.commit()
    print(f'Удалили слово {del_word} из бд')


@bot.message_handler(commands=['start'])   #начало работы с ботом, комнда "start"
def send_welcome(message):
    user_id = message.from_user.id
    user_name = message.chat.username
    if user_id not in known_users:
        known_users.extend([user_name, user_id])
        add_users(engine, user_id, user_name) #добавляем пользователя в бд
        userStep[user_id] = 0
        bot.send_message(user_id, f"""Привет, {user_name}! Добро пожаловать в Бот!
                                    \nОтправь /help и выбери одну, чтобы ознакомиться с правилами!""")


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, """Если тебе сложно дается запоминать новые слов, я тебе помогу! \
    У тебя есть возможность создать свою собственную базу обучения. Тебе будут даны 10 слов для их изучения. \
    Ты можешь добавить или удалить слово в любой момент, чтобы обучение было более эффективным.\n
                                      \nУ меня есть несколько основных команд, но в будущем их будет больше:\n
                                      \n/cards - Мини игра для изучения слов в виде карточек.
                                      \n'Добавить слово ➕' - позволит добавть новое слово для изучения.
                                      \n'Удалить слово 🔙' - позволит удалить существующее слово.""")


@bot.message_handler(commands=['cards'])    #соманда "cards"
def buttons_card(message):
    chat_id = message.chat.id
    #Проверяем наличие необходимого минимума слов(4)
    words = random.sample(english_words, 4)
    print(f"Случайные слова: {words}")

    if not words or len(words) < 4:
        bot.send_message(chat_id, "Недостаточно слов для создания карточек!\nДобавьте новые через 'Добавить слово ➕'.")
        print("Слов недостаточно для создания карточек.")
        return

    global buttons
    markup = types.ReplyKeyboardMarkup(row_width=2)
    translate_word = random.choice(russian_words)
    target_word = 'Правильное слово'  #должно передаваться перевод русского слова
    # target_word = target_w.filter(Basic_words.russian_word == russian_word).all() ??????
    other_words = random.sample(english_words, 3)

    translate_word_button = types.KeyboardButton(target_word)
    other_words_buttons = [types.KeyboardButton(word) for word in other_words]

    buttons = [translate_word_button] + other_words_buttons
    random.shuffle(buttons)

    add_btn = types.KeyboardButton(Commands.add)
    delete_btn = types.KeyboardButton(Commands.delete)
    next_btn = types.KeyboardButton(Commands.next)
    buttons.extend([add_btn, delete_btn, next_btn])

    markup.add(*buttons)

    bot.send_message(message.chat.id, f"""Выбери верный перевод русского слова '{translate_word}'""", reply_markup=markup)

    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id,  message.chat.id) as data:
        data['translate_word'] = translate_word
        data['target_word'] = target_word
        data['other_words'] = other_words


@bot.message_handler(func=lambda message: message.text == Commands.add, content_types=['text'])
def add_card(message):
    bot.send_message(message.chat.id, """Вы выбрали команду 'Добавить слово'. \
                Напиши в чат слово на русском языке.\
                Пример сообщения: 'машина'""")
    russian_word = message.text

    bot.send_message(message.chat.id, f"""Продолжим. \
        Напиши в чат перевод слова {russian_word} на английском языке.\
        Пример сообщения: 'машина'""")
    english_word = message.text

    add_personal_word(engine, russian_word, english_word)

@bot.message_handler(func=lambda message: message.text == Commands.next, content_types=['text'])
def next_card(message):
    buttons_card(message)

@bot.message_handler(func=lambda message: message.text == Commands.delete, content_types=['text'])
def next_card(message):
    bot.send_message(message.chat.id, """Вы выбрали команду 'Удалить слово'. \
                Напиши в чат слово на русском языке или его перевод на английском.\
                Пример сообщения: 'машина' или 'car'""")

    delete_word(message.text)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    with bot.retrieve_data(message.from_user.id,  message.chat.id) as data:
        target_word = data['target_word']
        if message.text == target_word:
            bot.send_message(message.chat.id, 'Верно! Поздравляю, ты хорошо справился! ❤')
            buttons_card(message)

        elif message.text != target_word and message.text not in [Commands.next, Commands.delete, Commands.add]:
            bot.send_message(message.chat.id, 'Ошибка.❌ Не сдавайся, попробуй еще раз!')



if __name__ == '__main__':
    print(known_users)
