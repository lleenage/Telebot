import sqlalchemy
from sqlalchemy.orm import sessionmaker
from bot_func import bot
from sql_func import create_tables, Basic_words, Personal_words, User


DSN = f"postgresql://postgres:2709200227092002@localhost:5432/translation"
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)


Session = sessionmaker(bind=engine)
session = Session()

basic_word1 = Basic_words(rusian_word='You', english_word='Ты')
basic_word2 = Basic_words(rusian_word='Their', english_word='Их')
basic_word6 = Basic_words(rusian_word='She', english_word='Она')
basic_word5 = Basic_words(rusian_word='He', english_word='Он')
basic_word3 = Basic_words(rusian_word='We', english_word='Мы')
basic_word4 = Basic_words(rusian_word='they', english_word='Они')
basic_word7 = Basic_words(rusian_word='It', english_word='Это')
basic_word8 = Basic_words(rusian_word='Her', english_word='Её')
basic_word9 = Basic_words(rusian_word='His', english_word='Его')
basic_word10 = Basic_words(rusian_word='Your', english_word='Твое')
session.add_all([basic_word1, basic_word2, basic_word3, basic_word4, basic_word5, basic_word6, basic_word7, basic_word8, basic_word9, basic_word10])
session.commit()






session.close()

if __name__ == '__main__':
    print('Bot is running')
    bot.polling()