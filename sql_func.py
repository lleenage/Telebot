import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

id = sq.Column(sq.Integer, primary_key=True)

class Basic_words(Base):
    __tablename__ = 'basic_words'

    id = sq.Column(sq.Integer, primary_key=True)
    rusian_word = sq.Column(sq.String(length=40), unique=True)
    english_word = sq.Column(sq.String(length=40), unique=True)

    def __str__(self):
        return f'Basic words is {self.rusian_word} : {self.english_word}'



class Personal_words(Base):
    __tablename__ = "personal_words"

    id = sq.Column(sq.Integer, primary_key=True)
    rusian_word = sq.Column(sq.String(length=40), unique=True)
    english_word = sq.Column(sq.String(length=40), unique=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("user.id"), nullable=False)

    word = relationship(User, backref="words")

    def __str__(self):
        return f'Your words is {self.rusian_word}: {self.english_word}'
    



def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)