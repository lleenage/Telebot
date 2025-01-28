import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sql_func import create_tables, Basic_words, User
# import psycopg2


DSN = f"postgresql://postgres:2709200227092002@localhost:5432/translation"
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

def add_basic_word(engine, russian_word: str, english_word: str): #добавляем основные 10 слов
    session = (sessionmaker(bind=engine))()
    session.add(Basic_words(russian_word=russian_word, english_word=english_word))
    session.commit()
    session.close()

add_basic_word(engine, 'Масло', 'Oil')
add_basic_word(engine, 'Магазин', 'Shop')
add_basic_word(engine, 'Собака', 'Dog')
add_basic_word(engine, 'Весна', 'Spring')
add_basic_word(engine, 'Дом', 'House')
add_basic_word(engine, 'Вода', 'Water')
add_basic_word(engine, 'Имя', 'Name')
add_basic_word(engine, 'Дорога', 'Road')
add_basic_word(engine, 'Рука', 'Arm')
add_basic_word(engine, 'Одежда', 'Clothes')

# session = (sessionmaker(bind=engine))()
# target_w = session.query(Basic_words.english_word).filter(Basic_words.russian_word == russian_word).all()
#
# session.close()

if __name__ == '__main__':
    from PyCode.bot_func import bot, russian_words

    print('Bot is running')
    bot.polling()