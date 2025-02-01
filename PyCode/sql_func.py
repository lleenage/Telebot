import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.BigInteger, unique=True)
    name = sq.Column(sq.String(length=80))

    def __str__(self):
        return f"Пользовтель номер {self.id}: name:'{self.name}', user_id:'{self.user_id}'"


class Personal_words(Base):
    __tablename__ = "personal_words"

    id = sq.Column(sq.Integer, primary_key=True)
    russian_word = sq.Column(sq.String(length=40), unique=True)
    english_word = sq.Column(sq.String(length=40), unique=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("user.id"), nullable=False)

    user = relationship(User, backref="personal_words")

    def __str__(self):
        return f'Слово номер {self.id} "{self.russian_word}: {self.english_word}"'


class Basic_words(Base):
    __tablename__ = 'basic_words'

    id = sq.Column(sq.Integer, primary_key=True)
    russian_word = sq.Column(sq.String(length=40), unique=True)
    english_word = sq.Column(sq.String(length=40), unique=True)

    def __str__(self):
        return f'{self.id} базовое слово "{self.russian_word}: {self.english_word}"'

# class Personal_Basic_words(Base):
#     __tablename__ = 'personal_basic_words'
#
#     id = sq.Column(sq.Integer, primary_key=True)
#     basic_word_id = sq.Column(sq.Integer, sq.ForeignKey("basic_words.id"), nullable=False)
#     personal_word_id = sq.Column(sq.Integer, sq.ForeignKey("personal_words.id"), nullable=False)
#
#     personal_words = relationship(Personal_words, backref='basic_words')
#     basic_words = relationship(Personal_words, backref='personal_words')


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)