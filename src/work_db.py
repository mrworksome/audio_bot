from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String)
    nick_name = Column(String)


class AudioMessage(Base):
    __tablename__ = 'audio_message'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(User.user_id))
    message_id = Column(Integer)
    audio_path = Column(String)


class PhotoMessage(Base):
    __tablename__ = 'photo_message'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(User.user_id))
    message_id = Column(Integer)
    photo_path = Column(String)

