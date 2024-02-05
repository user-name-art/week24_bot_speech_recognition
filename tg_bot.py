import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from environs import Env
from google_dialogflow_api import detect_intent_texts
from log_handler import TelegramLogsHandler


env = Env()
env.read_env()

LANGUAGE_CODE = 'ru-RU'
PROJECT_ID = env.str('GOOGLE_PROJECT_ID')
SESSION_ID = env.str('TG_USER_ID')
BOT_TOKEN = env.str('TG_BOT_TOKEN')

logger = logging.getLogger('Logger')
logger.setLevel(logging.INFO)
logger.addHandler(TelegramLogsHandler(BOT_TOKEN, SESSION_ID))


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def answer_to_message(update: Update, context: CallbackContext) -> None:
    try:
        question_is_unclear, smart_answer = detect_intent_texts(
            PROJECT_ID,
            SESSION_ID,
            update.message.text,
            LANGUAGE_CODE
        )
        update.message.reply_text(smart_answer)
    except Exception as err:
        logger.error('У Telegram-бота возникла следующая ошибка:')
        logger.exception(err)


def main() -> None:
    updater = Updater(BOT_TOKEN)
    logger.info('tg bot started')
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, answer_to_message))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
