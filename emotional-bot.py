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


# linear transformation
def linear(n):
    low_value = 0.5
    high_value = 0.75
    less_balls = 3
    more_balls = 7
    result = less_balls + (more_balls - less_balls) * ((n - low_value)/(high_value - low_value))
    if result < 0:
        result = 0
    return result


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi! I am a bot that analyzes what people will think you are feeling through your text.')
    bot.sendMessage(update.message.chat_id, text='Just send me your text.')


def create_emotion_text(response):
    emotion_tone = filter(lambda x: x['category_id'] == 'emotion_tone',
            response['document_tone']['tone_categories'])[0]
    tones = emotion_tone['tones']

    text = u'The emotions in your text seems to be:\n'

    for tone in tones:
        progress = list(u'************')
        position = int(round(linear(tone['score'])))
        progress[position] = u'@'
        text += u'\n' + u''.join(progress) + u' ' + unicode(tone['tone_name'])

        text += u'\n'

    return text


def analyze(bot, update):
    tone_analyzer = ToneAnalyzerV3Beta(
        username=config('USERNAME'),
        password=config('PASSWORD'),
        version='2016-05-19',
        url='https://gateway.watsonplatform.net/tone-analyzer/api'
        )

    response = tone_analyzer.tone(text=update.message.text)

    text = create_emotion_text(response)
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
