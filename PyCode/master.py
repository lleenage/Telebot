import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sql_func import User, Personal_words, Basic_words, create_tables
import telebot
from telebot import types
from telebot.handler_backends import StatesGroup, State
import random
from private.confirm import TOKEN_TELEBOT

DSN = f"postgresql://postgres:2709200227092002@localhost:5432/translation"
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

session = (sessionmaker(bind=engine))()

personal_russian_words = []   #список с персональными русскими словами
personal_english_words = []   #список с персональными английскими словами
english_cards = []  #список со всеми английскими словами, использующийся для создания карточек
russian_cards = []  #список со всеми русскими словами, использующийся для создания карточек


#Функия получения перевода слов
def get_target_word(translate_word: str) -> str:
    if translate_word in basic_russian_words:
        target_w = session.query(Basic_words.english_word).filter(Basic_words.russian_word == translate_word).all()[0][0]
        return target_w
    elif translate_word in basic_english_words:
        target_w = session.query(Basic_words.russian_word).filter(Basic_words.english_word == translate_word).all()[0][0]
        return target_w
    elif translate_word in personal_english_words:
        target_w = session.query(Personal_words.russian_word).filter(Personal_words.english_word == translate_word).all()[0][0]
        return target_w
    elif translate_word in personal_russian_words:
        target_w = session.query(Personal_words.english_word).filter(Personal_words.russian_word == translate_word).all()[0][0]
        return target_w
    else:
        return 'Нет такого слова'
#Функция добавления нового пользователя
def add_users(user_id: int, user_name: str):   #функция добавляющая пользователя в бд с параметрами user_id, user_name
    session.add(User(user_id=user_id, name=user_name))
    for i in session.query(User).all():
        print(i)
    session.commit()
#Функция добавления персональных слов пользователем
def add_personal_word(any_russian_word: str, any_english_word: str, uid: int) -> str: #функция для добавления слов в бд
    for u_id in session.query(User.id).filter(User.user_id == uid).all():
        if any_russian_word not in session.query(Personal_words.russian_word).all():
            session.add(Personal_words(russian_word=any_russian_word, english_word=any_english_word, user_id=u_id[0]))
            session.commit()
            for i in session.query(Personal_words).filter(Personal_words.russian_word == any_russian_word).all():
                result = f'{i.russian_word} - {i.english_word}'
                personal_russian_words.append(any_russian_word)
                russian_cards.append(any_russian_word)
                personal_english_words.append(any_english_word)
                english_cards.append(any_english_word)
                return f'"{result}" успешно добавлено.'
        else:
            return f'Слово "{any_russian_word}" уже было добавлено ранее'
#Функция для удаления персональных слов пользователем
def delete_word(del_word: str, uid: int) -> int:
    for id_ in session.query(User.id).filter(User.user_id == uid).all():
        id_ = id_[0]
        if del_word in basic_english_words or del_word in basic_russian_words:
            print(f'Попытка удалить слово "{del_word}", что находится в базовых словах.')
            return 0
        elif del_word in personal_russian_words:
            session.query(Personal_words).filter(Personal_words.russian_word == del_word).filter(Personal_words.user_id==id_).delete() # удаляем объект
            session.commit()
            del_eng_word = get_target_word(del_word)
            personal_russian_words.remove(del_word)
            personal_english_words.remove(del_eng_word)
            english_cards.remove(del_eng_word)
            russian_cards.remove(del_word)
            print(f'Удалили слово "{del_word}" из бд')
            return session.query(Personal_words).filter(Personal_words.user_id==id_).all()[0]
        elif del_word in personal_english_words:
            session.query(Personal_words).filter(Personal_words.english_word == del_word).filter(Personal_words.user_id==id_).delete() # удаляем объект
            session.commit()
            del_russ_word = get_target_word(del_word)
            personal_english_words.remove(del_word)
            personal_russian_words.remove(del_russ_word)
            english_cards.remove(del_word)
            russian_cards.remove(del_russ_word)
            print(f'Удалили слово "{del_word}" из бд')
            return session.query(Personal_words).filter(Personal_words.user_id==id_).all()[0]
        else:
            print(f'Попытка удалить слово "{del_word}", которое не существует ни в одном из бд.')
            return 1
#Функция для добавления базовых слов
def add_basic_word(russian_word: str, english_word: str): #добавляем основные 10 слов
    session.add(Basic_words(russian_word=russian_word, english_word=english_word))
    session.commit()

add_basic_word('Масло', 'Oil')
add_basic_word('Магазин', 'Shop')
add_basic_word('Собака', 'Dog')
add_basic_word('Весна', 'Spring')
add_basic_word('Дом', 'House')
add_basic_word('Вода', 'Water')
add_basic_word('Имя', 'Name')
add_basic_word('Дорога', 'Road')
add_basic_word('Рука', 'Arm')
add_basic_word('Одежда', 'Clothes')

session.close()


telebot_token = TOKEN_TELEBOT
bot = telebot.TeleBot(telebot_token)

buttons = []
known_users = []

class Commands:
    add = 'Добавить слово ➕🆕'
    delete = 'Удалить слово 🔙'
    next = 'Следующее слово ⏭'

class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    other_words = State()


@bot.message_handler(commands=['start'])   #начало работы с ботом, комнда "start"
def send_welcome(message):
    user_id = message.from_user.id
    user_name = message.chat.username
    if user_id not in known_users:
        known_users.extend([user_name, user_id])
        add_users(user_id, user_name) #добавляем пользователя в бд
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
                                      \n"Удалить слово 🔙" - позволит удалить существующее слово. К сожалению удалть можно только те слова, которые вы добавляли самостоятельно.''')


@bot.message_handler(commands=['cards'])    #соманда "cards"
def buttons_card(message):
    chat_id = message.chat.id
    #Проверяем наличие необходимого минимума английских слов(4)
    random_words = random.sample(english_cards, 4)
    # words = random.sample(english_cards, 4)

    if not random_words or len(random_words) < 4:
        bot.send_message(chat_id, 'Недостаточно слов для создания карточек!\nДобавьте новые через "Добавить слово ➕🆕".')
        print('Слов недостаточно для создания карточек.')
    else:
        global buttons
        buttons = []
        markup = types.ReplyKeyboardMarkup(row_width=2)
        translate_word = random.choice(russian_cards)
        target_word = get_target_word(translate_word)
        other_words = random.sample(english_cards, 3)

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
        print(add_personal_word(add_russian_word, add_english_word, user_id))
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
    # try:
    if delete_word(delate_word, uid) is str:
        bot.send_message(message.chat.id, f'Слово "{delate_word}" было успешно удалено.')
    elif delete_word(delate_word, uid) == 0:
        bot.send_message(message.chat.id, f'Слово "{delate_word}" не может быть удалено, оно находится в общем доступе.')
    elif delete_word(delate_word, uid) == 1:
        bot.send_message(message.chat.id, f'Слово "{delate_word}" не может быть удалено. Возможно, вы его еще не добавили.')
    # except:
    #     print('Ошибка')

@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    with bot.retrieve_data(message.from_user.id,  message.chat.id) as data:
        target_word = data['target_word']
        if message.text == target_word:
            bot.send_message(message.chat.id, 'Верно!✅ Поздравляю, ты хорошо справился!')

        elif message.text != target_word and message.text not in [Commands.next, Commands.delete, Commands.add]:
            bot.send_message(message.chat.id, 'Ошибка.❌ Не сдавайся, попробуй еще раз!')

basic_russian_words = [i.russian_word for i in (sessionmaker(bind=engine))().query(Basic_words).all()] #список с базовыми русскими словами
basic_english_words = [i.english_word for i in (sessionmaker(bind=engine))().query(Basic_words).all()] #список с базовыми английскими словами


if __name__ == '__main__':
    add_russian_word = ['Масло', 'Магазин', 'Собака', 'Весна', 'Дом', 'Вода', 'Имя', 'Дорога', 'Рука', 'Одежда']
    add_english_word = ['Oil', 'Shop', 'Dog', 'Spring', 'House', 'Water', 'Name', 'Road', 'Arm', 'Clothes']

    for r in add_russian_word:
        russian_cards.append(r)
    for e in add_english_word:
        english_cards.append(e)

    print('Bot is running')
    bot.polling()