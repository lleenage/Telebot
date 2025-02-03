import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sql_func import User, Personal_words, Basic_words, create_tables

DSN = f"postgresql://postgres:2709200227092002@localhost:5432/translation"
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

session = (sessionmaker(bind=engine))()

personal_russian_words = []   #список с персональными русскими словами
personal_english_words = []   #список с персональными английскими словами
english_cards = []  #список со всеми английскими словами, использующийся для создания карточек
russian_cards = []  #список со всеми русскими словами, использующийся для создания карточек

basic_russian_words = [i.russian_word for i in (sessionmaker(bind=engine))().query(Basic_words).all()] #список с базовыми русскими словами
basic_english_words = [i.english_word for i in (sessionmaker(bind=engine))().query(Basic_words).all()] #список с базовыми английскими словами

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

session.close()


if __name__ == '__main__':
    from PyCode.bot_func import bot

    add_russian_word = ['Масло', 'Магазин', 'Собака', 'Весна', 'Дом', 'Вода', 'Имя', 'Дорога', 'Рука', 'Одежда']
    add_english_word = ['Oil', 'Shop', 'Dog', 'Spring', 'House', 'Water', 'Name', 'Road', 'Arm', 'Clothes']

    for r in add_russian_word:
        russian_cards.append(r)
    for e in add_english_word:
        english_cards.append(e)

    print('russian_cards:', russian_cards)
    print('english_cards:', english_cards)

    print('Bot is running')
    bot.polling()