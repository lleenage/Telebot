import telebot
import random
from dotenv import load_dotenv
import os
from telebot import types 
from telebot.handler_backends import StatesGroup, State
from sql_func import create_tables, Basic_words, Personal_words, User



dotenv_path = "private/confirm.env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

telebot_token = os.getenv('TOKEN_TELEBOT')
# yandex_token = 'YANDEX_TOKEN'

bot = telebot.TeleBot(telebot_token)


class Commands:
    add = 'Добавить слово ➕'
    delete = 'Удалить слово 🔙'
    next = 'Следующее слово ⏭'

class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    other_words = State()



@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Hi! Welcome to Assistant Bot!\nI will help you with your English.\n\nПривет! Добро пожаловать в Бот! Я помогу тебе с изучением английского.')
    bot.send_message(message.chat.id, "I have a few commands. Print /help and choose one.\n\nУ меня есть несколько команд. Отправь /help и выбери одну.")


@bot.message_handler(commands=['cards'])
def buttons_card(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    russian_word = 'Мир'
    target_word = 'World'
    other_words = ['Car', 'Word', 'Cat']

    translate_word_button = types.KeyboardButton(target_word)
    other_words_buttons = [types.KeyboardButton(word) for word in other_words]

    buttons = [translate_word_button] + other_words_buttons
    random.shuffle(buttons)

    add_btn = types.KeyboardButton(Commands.add)
    delete_btn = types.KeyboardButton(Commands.delete)
    next_btn = types.KeyboardButton(Commands.next)
    buttons.extend([add_btn, delete_btn, next_btn])

    markup.add(*buttons)

    bot.send_message(message.chat.id, f"Guese the translation of the russian word '{russian_word}'\n\nУгадай перевод русского слова '{russian_word}'", reply_markup=markup)

    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id,  message.chat.id) as data:
        data['translate_word'] = russian_word
        data['target_word'] = target_word
        data['other_words'] = other_words



@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, 'So. Now i have 2 commands for you:\n\nИ так. Сейчас у меня есть 2 команды для тебя:\n\n/cards - Мини игра для изучения слов в виде карточек\n/grammas - пока не сделала')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    with bot.retrieve_data(message.from_user.id,  message.chat.id) as data:
        target_word = data['target_word']
    if message.text == target_word:
        bot.send_message(message.chat.id, 'Верно! Поздравляю, ты хорошо справился! ❤')
    else:
        bot.send_message(message.chat.id, 'Ошибка.❌ Не сдавайся, попробуй еще раз!')
