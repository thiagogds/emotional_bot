#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to analyze emotions in Telegram messages
# This program is dedicated to the public domain under the CC0 license.

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from watson_developer_cloud import ToneAnalyzerV3Beta
from decouple import config

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def create_emotion_text(response, emotion_title, category_id):
    emotion_tone = filter(lambda x: x['category_id'] == category_id, response['document_tone']['tone_categories'])[0]
    tones = emotion_tone['tones']

    text = emotion_title
    text += ':\n'

    for tone in tones:
        text += tone['tone_name'] + ": " + str(tone['score'] * 100) + "%"
        text += '\n'

    return text


def analyze(bot, update):
    tone_analyzer = ToneAnalyzerV3Beta(
        username=config('USERNAME'),
        password=config('PASSWORD'),
        version='2016-05-19',
        url='https://gateway.watsonplatform.net/tone-analyzer/api'
        )

    response = tone_analyzer.tone(text=update.message.text)

    text = create_emotion_text(response, 'Emotion tones', 'emotion_tone')
    bot.sendMessage(update.message.chat_id, text=text)

    text = create_emotion_text(response, 'Language tones', 'language_tone')
    bot.sendMessage(update.message.chat_id, text=text)

    text = create_emotion_text(response, 'Social tones', 'social_tone')
    bot.sendMessage(update.message.chat_id, text=text)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(config('BOT_HASH'))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - analyze the message on Telegram
    dp.add_handler(MessageHandler([Filters.text], analyze))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
