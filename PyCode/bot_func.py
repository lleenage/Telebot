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
personal_russian_words = []
personal_english_words = []

basic_russian_words = [i.russian_word for i in (sessionmaker(bind=engine))().query(Basic_words).all()]
basic_english_words = [i.english_word for i in (sessionmaker(bind=engine))().query(Basic_words).all()]  #передаем сюда и базовые и персональные русские слова
(sessionmaker(bind=engine))().close()

class Commands:
    add = 'Добавить слово ➕🆕'
    delete = 'Удалить слово 🔙'
    next = 'Следующее слово ⏭'

class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    other_words = State()

def get_target_word(translate_word: str) -> str:
    session = (sessionmaker(bind=engine))()
    if translate_word in basic_russian_words:
        target_w = session.query(Basic_words.english_word).filter(Basic_words.russian_word == translate_word).all()[0][0]
        session.close()
        return target_w
    elif translate_word in basic_english_words:
        target_w = session.query(Basic_words.russian_word).filter(Basic_words.english_word == translate_word).all()[0][0]
        session.close()
        return target_w
    elif translate_word in personal_english_words:
        target_w = session.query(Personal_words.russian_word).filter(Personal_words.english_word == translate_word).all()[0][0]
        session.close()
        return target_w
    elif translate_word in personal_russian_words:
        target_w = session.query(Personal_words.english_word).filter(Personal_words.russian_word == translate_word).all()[0][0]
        session.close()
        return target_w
    else:
        return 'Нет такого слова'

def get_user_step(user_name: str, user_id: int) -> int:
    if user_id in userStep:
        return userStep[user_id] #должен быть 0
    else:
        known_users.extend([user_name, user_id])
        userStep[user_id] = 0
        print('Новый пользователь, который eще не использовал "/start"')
        return 0

def add_users(engine, user_id: int, user_name: str):   #функция добавляющая пользователя в бд с параметрами user_id, user_name
    session = (sessionmaker(bind=engine))()
    session.add(User(user_id=user_id, name=user_name))
    for i in session.query(User).all():
        print(i)
    session.commit()
    session.close()

def add_personal_word(engine, any_russian_word: str, any_english_word: str, uid: int) -> str: #функция для добавления слов в бд
    session = (sessionmaker(bind=engine))()
    for u_id in session.query(User.id).filter(User.user_id == uid).all():
        if any_russian_word not in session.query(Personal_words.russian_word).all():
            session.add(Personal_words(russian_word=any_russian_word, english_word=any_english_word, user_id=u_id[0]))
            session.commit()
            for i in session.query(Personal_words).filter(Personal_words.russian_word == any_russian_word).all():
                result = f'{i.russian_word} - {i.english_word}'
                session.close()
                personal_russian_words.append(any_russian_word)
                personal_english_words.append(any_english_word)
                return f'"{result}" успешно добавлено.'
        else:
            return f'Слово "{any_russian_word}" уже было добавлено ранее'


def delete_word(del_word: str, uid: int) -> int:
    session = (sessionmaker(bind=engine))()
    for id_ in session.query(User.id).filter(User.user_id == uid).all():
        id_ = id_[0]
        if del_word in basic_english_words or del_word in basic_russian_words:
            print(f'Попытка удалить слово "{del_word}", что находится в базовых словах.')
            return 0
        elif del_word in personal_russian_words:
            session.query(Personal_words).filter(Personal_words.russian_word == del_word).filter(Personal_words.user_id==id_).delete() # удаляем объект
            session.commit()
            session.close()
            del_eng_word = get_target_word(del_word)
            personal_russian_words.remove(del_word)
            personal_english_words.remove(del_eng_word)
            print(f'Удалили слово "{del_word}" из бд')
            return session.query(Personal_words).filter(Personal_words.user_id==id_).all()
        elif del_word in personal_english_words:
            session.query(Personal_words).filter(Personal_words.english_word == del_word).filter(Personal_words.user_id==id_).delete() # удаляем объект
            session.commit()
            session.close()
            print('Этап 1', 'Удалили из бд')
            del_russ_word = get_target_word(del_word)
            print('Этап 2', del_russ_word)
            personal_english_words.remove(del_word)
            print('Этап 3', personal_english_words)
            personal_russian_words.remove(del_russ_word)
            print(f'Удалили слово "{del_word}" из бд')
            return session.query(Personal_words).filter(Personal_words.user_id==id_).all()
        else:
            print(f'Попытка удалить слово "{del_word}", которое не существует ни в одном из бд.')
            return 1


@bot.message_handler(commands=['start'])   #начало работы с ботом, комнда "start"
def send_welcome(message):
    user_id = message.from_user.id
    user_name = message.chat.username
    if user_id not in known_users:
        known_users.extend([user_name, user_id])
        add_users(engine, user_id, user_name) #добавляем пользователя в бд
        userStep[user_id] = 0
        bot.send_message(user_id, f'''Привет, {user_name}! Добро пожаловать в Бот!
                                    \nОтправь /help и выбери одну, чтобы ознакомиться с правилами!''')


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, '''Если тебе сложно дается запоминать новые слов, я тебе помогу!
                                      \nУ тебя есть возможность создать свою собственную базу обучения. Тебе будут даны 10 базовых слов для их изучения.
                                      \nТы можешь добавить или удалить слово в любой момент, чтобы обучение было более эффективным.(Базовые слова удалению не подлежат.)\n
                                      \nУ меня есть несколько основных команд:\n
                                      \n/cards - Мини игра для изучения слов в виде карточек.
                                      \n"Добавить слово ➕🆕" - позволит добавть новое слово для изучения.
                                      \n"Удалить слово 🔙" - позволит удалить существующее слово. К сожалению базовые слова, не добавленые лично вами, удалить невозможно.''')


@bot.message_handler(commands=['cards'])    #соманда "cards"
def buttons_card(message):
    chat_id = message.chat.id
    #Проверяем наличие необходимого минимума слов(4)
    words = random.sample(basic_english_words, 4)

    if not words or len(words) < 4:
        bot.send_message(chat_id, 'Недостаточно слов для создания карточек!\nДобавьте новые через "Добавить слово ➕🆕".')
        print('Слов недостаточно для создания карточек.')
    else:
        global buttons
        buttons = []
        markup = types.ReplyKeyboardMarkup(row_width=2)
        translate_word = random.choice(basic_russian_words)
        target_word = get_target_word(translate_word)
        other_words = random.sample(basic_english_words, 3)

        target_word_button = types.KeyboardButton(target_word)
        other_words_buttons = [types.KeyboardButton(word) for word in other_words]

        buttons = [target_word_button] + other_words_buttons
        random.shuffle(buttons)

        add_btn = types.KeyboardButton(Commands.add)
        delete_btn = types.KeyboardButton(Commands.delete)
        next_btn = types.KeyboardButton(Commands.next)
        buttons.extend([add_btn, delete_btn, next_btn])

        markup.add(*buttons)

        bot.send_message(message.chat.id, f'Выбери верный перевод русского слова "{translate_word}".', reply_markup=markup)

        bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
        with bot.retrieve_data(message.from_user.id,  message.chat.id) as data:
            data['translate_word'] = translate_word
            data['target_word'] = target_word
            data['other_words'] = other_words


@bot.message_handler(func=lambda message: message.text == Commands.add, content_types=['text'])
def add_word(message):
    print('Попытка добавить слово')
    user_name = message.chat.username
    if user_name not in known_users:
        print('Новый пользователь, который eще не использовал "/start"')
        bot.send_message(message.chat.id, 'Сначала используйте функцию /start')
    else:
        bot.send_message(message.chat.id, '''Вы выбрали команду "Добавить слово ➕🆕".
                            \nНапиши в чат слово на русском языке.
                            \nПример сообщения: "Машина"''')
        bot.register_next_step_handler(message, get_russ_word)
def get_russ_word(message):
    print('Пользователь ввел слово', message.text)
    global add_russian_word
    add_russian_word = message.text
    bot.send_message(message.chat.id, f'''Продолжим.
        \nНапиши в чат перевод слова "{add_russian_word}" на английском языке.
        \nПример сообщения: "Car"''')
    bot.register_next_step_handler(message, get_eng_word)
def get_eng_word(message):
    print('Пользователь ввел слово', message.text)
    add_english_word = message.text
    user_id = message.from_user.id
    if add_russian_word not in personal_russian_words and add_english_word not in personal_english_words:
        print(add_personal_word(engine, add_russian_word, add_english_word, user_id))
        bot.send_message(message.chat.id, f'Успешно добавлено слово "{add_russian_word}" с переводом "{add_english_word}" ✅')
    else:
        bot.send_message(message.chat.id,
                         f'Не удалось добавить слово, возможно слово "{add_russian_word}" уже было добавлено ранее.')
        print(f'Попытка добавить существующее слово "{add_russian_word}"')

@bot.message_handler(func=lambda message: message.text == Commands.next, content_types=['text'])
def next_card(message):
    buttons_card(message)


@bot.message_handler(func=lambda message: message.text == Commands.delete, content_types=['text'])
def del_word(message):
    print('Попытка удалить слово.')
    user_name = message.chat.username
    if user_name not in known_users:
        print('Новый пользователь, который eще не использовал "/start"')
        bot.send_message(message.chat.id, 'Сначала используйте функцию /start')
    else:
        bot.send_message(message.chat.id, '''Вы выбрали команду "Удалить слово 🔙". 
                    \nНапиши в чат слово на русском языке или его перевод на английском.
                    \nПример сообщения: "Mашина" или "Car"''')
        bot.register_next_step_handler(message, get_del_word)
def get_del_word(message):
    delate_word = message.text
    uid = message.from_user.id
    try:
        if delete_word(delate_word, uid) is str:
            bot.send_message(message.chat.id, f'Слово "{delate_word}" было успешно удалено.')
        elif delete_word(delate_word, uid) == 0:
            bot.send_message(message.chat.id, f'Слово "{delate_word}" не может быть удалено, оно находится в общем доступе.')
        elif delete_word(delate_word, uid) == 1:
            bot.send_message(message.chat.id, f'Слово "{delate_word}" не может быть удалено. Возможно, вы его еще не добавили.')
    except:
        print('Ошибка')

@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    with bot.retrieve_data(message.from_user.id,  message.chat.id) as data:
        target_word = data['target_word']
        if message.text == target_word:
            bot.send_message(message.chat.id, 'Верно!✅ Поздравляю, ты хорошо справился! ❤')

        elif message.text != target_word and message.text not in [Commands.next, Commands.delete, Commands.add]:
            bot.send_message(message.chat.id, 'Ошибка.❌ Не сдавайся, попробуй еще раз!')
