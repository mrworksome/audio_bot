# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import sys

from pydub import AudioSegment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from telegram.error import InvalidToken
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

from src.face_detector import FaceDetector
from src.proxy import proxy
from src.work_db import User, AudioMessage, Base, PhotoMessage


class AudioBot:
    def __init__(self, token):
        super(AudioBot, self).__init__()

        # logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)

        # BD
        engine = create_engine('sqlite:///dbase.db')
        connection = engine.connect()
        session = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=connection.engine)
        self.session = session()

        self.face_check = FaceDetector()

        self.updater = Updater(
            token=token,
            # request_kwargs=proxy,
            use_context=True
        )

        self.dispatcher = self.updater.dispatcher

        audio_handler = MessageHandler(Filters.voice , self.voice_handler)
        photo_handler = MessageHandler(Filters.photo, self.photo_handler)

        self.dispatcher.add_handler(audio_handler)
        self.dispatcher.add_handler(photo_handler)

    def voice_handler(self, update, context: CallbackContext):
        """
        download voice message and convert to .wav with framerate 16000

        """
        # user parameters
        user_id = update.message.from_user.id
        nickname = update.message.from_user.username
        name = f'{update.message.from_user.first_name} {update.message.from_user.last_name}'

        # voice file id
        file_id = update.message.voice.file_id

        src_filename = f'./audio_files/{file_id}.ogg'
        dest_filename = f'./audio_files/{file_id}.wav'
        if file_id:
            update.message.reply_text("There voice message is received.")
            file = context.bot.get_file(file_id)
            file.download(src_filename)

            # convert ogg to wav
            AudioSegment.from_file(src_filename).export(dest_filename, format="wav")
            my_sound = AudioSegment.from_file(dest_filename).set_frame_rate(16000)
            my_sound.export(dest_filename, format="wav")

            # remove download file to convert
            os.remove(src_filename)

            user = self.session.query(User).filter(User.user_id == user_id).first()
            if not user:
                user = User(user_id=user_id, nick_name=nickname, name=name)
                self.session.add(user)

            self.session.add(
                AudioMessage(user_id=user.user_id, message_id=update.message.message_id,
                             audio_path=os.path.abspath(dest_filename)))
            self.session.commit()

    def photo_handler(self, update, context):
        user_id = update.message.from_user.id
        nickname = update.message.from_user.username
        name = f'{update.message.from_user.first_name} {update.message.from_user.last_name}'

        photo_file_id = update.message.photo[-1].file_id
        photo_file_path = f'./photo_files/{photo_file_id}.jpg'

        if photo_file_id:
            update.message.reply_text("Get the photo file")
            file = context.bot.get_file(photo_file_id)
            file.download(photo_file_path)
            if self.face_check.detect_faces(photo_file_path):
                update.message.reply_text("There faces on the photo")

                user = self.session.query(User).filter(User.user_id == user_id).first()
                if not user:
                    user = User(user_id=user_id, nick_name=nickname, name=name)
                    self.session.add(user)

                self.session.add(
                    PhotoMessage(user_id=user.user_id, message_id=update.message.message_id,
                                 photo_path=os.path.abspath(photo_file_path)))
                self.session.commit()

            else:
                update.message.reply_text("There NO faces on the photo")
                os.remove(photo_file_path)

    def run(self):
        self.updater.start_polling()
        return


if __name__ == "__main__":
    from common import get_config, CONFIG_PATH

    settings = get_config()

    if not CONFIG_PATH:
        logging.info("Error, no config file")
        sys.exit(1)

    if ("main" not in settings) or ("token" not in settings["main"]):
        logging.info("Error, no token in config file")

    try:
        a = AudioBot(settings["main"]["token"])
        a.run()
    except (InvalidToken, ValueError):
        print(
            'Critical Error > Telegram Access Token is invalid.'
            ' Terminal halted.\nCheck the configuration file.')
        exit()
    finally:
        print("Bot running...")
