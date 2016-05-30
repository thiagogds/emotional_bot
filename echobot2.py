#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.

"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
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


def echo(bot, update):
    tone_analyzer = ToneAnalyzerV3Beta(
        username=config('USERNAME'),
        password=config('PASSWORD'),
        version='2016-02-11',
        url='https://gateway.watsonplatform.net/tone-analyzer/api'
        )

    moods = {
        'Anger': u'😡',
        'Disgust': u'😷',
        'Fear': u'😱',
        'Joy': u'😄',
        'Sadness': u'😢',
    }

    response = tone_analyzer.tone(text=update.message.text)
    emotion_tone = filter(lambda x: x['category_id'] == 'emotion_tone', response['document_tone']['tone_categories'])[0]
    tones = emotion_tone['tones']
    text = ''
    for tone in tones:
        text += moods[tone['tone_name']] + " " + tone['tone_name'] + ": " + str(tone['score'] * 100) + "%"
        text += '\n'

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

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler([Filters.text], echo))

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
